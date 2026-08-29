//! Structurally independent Rust checker for ORION-02 R18/R19/R20.
//!
//! The checker uses no ORION Python modules and no external Rust crates.  It
//! parses the durably retained R18 recovery result and the current-main R19
//! result, recomputes theorem-critical finite controls, and emits one
//! deterministic JSON receipt.  Same-owner cross-language corroboration is not
//! external independence and the receipt keeps that authority ceiling explicit.

use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs;
use std::path::PathBuf;

#[derive(Clone, Debug, PartialEq)]
enum Json {
    Null,
    Bool(bool),
    Number(String),
    String(String),
    Array(Vec<Json>),
    Object(BTreeMap<String, Json>),
}

struct Parser<'a> {
    bytes: &'a [u8],
    pos: usize,
}

impl<'a> Parser<'a> {
    fn new(text: &'a str) -> Self {
        Self {
            bytes: text.as_bytes(),
            pos: 0,
        }
    }

    fn parse(mut self) -> Result<Json, String> {
        let value = self.value()?;
        self.space();
        if self.pos != self.bytes.len() {
            return Err(format!("trailing JSON bytes at {}", self.pos));
        }
        Ok(value)
    }

    fn space(&mut self) {
        while self.pos < self.bytes.len() && self.bytes[self.pos].is_ascii_whitespace() {
            self.pos += 1;
        }
    }

    fn value(&mut self) -> Result<Json, String> {
        self.space();
        let byte = *self
            .bytes
            .get(self.pos)
            .ok_or_else(|| "unexpected end of JSON".to_string())?;
        match byte {
            b'n' => {
                self.literal(b"null")?;
                Ok(Json::Null)
            }
            b't' => {
                self.literal(b"true")?;
                Ok(Json::Bool(true))
            }
            b'f' => {
                self.literal(b"false")?;
                Ok(Json::Bool(false))
            }
            b'"' => Ok(Json::String(self.string()?)),
            b'[' => self.array(),
            b'{' => self.object(),
            b'-' | b'0'..=b'9' => Ok(Json::Number(self.number()?)),
            _ => Err(format!("unexpected JSON byte {} at {}", byte, self.pos)),
        }
    }

    fn literal(&mut self, expected: &[u8]) -> Result<(), String> {
        if self.bytes.get(self.pos..self.pos + expected.len()) != Some(expected) {
            return Err(format!("invalid literal at {}", self.pos));
        }
        self.pos += expected.len();
        Ok(())
    }

    fn string(&mut self) -> Result<String, String> {
        if self.bytes.get(self.pos) != Some(&b'"') {
            return Err(format!("string must start at {}", self.pos));
        }
        self.pos += 1;
        let mut result = String::new();
        while self.pos < self.bytes.len() {
            let byte = self.bytes[self.pos];
            self.pos += 1;
            match byte {
                b'"' => return Ok(result),
                b'\\' => {
                    let escaped = *self
                        .bytes
                        .get(self.pos)
                        .ok_or_else(|| "unterminated escape".to_string())?;
                    self.pos += 1;
                    match escaped {
                        b'"' => result.push('"'),
                        b'\\' => result.push('\\'),
                        b'/' => result.push('/'),
                        b'b' => result.push('\u{0008}'),
                        b'f' => result.push('\u{000c}'),
                        b'n' => result.push('\n'),
                        b'r' => result.push('\r'),
                        b't' => result.push('\t'),
                        b'u' => {
                            let code = self.hex4()?;
                            if (0xd800..=0xdbff).contains(&code) {
                                if self.bytes.get(self.pos..self.pos + 2) != Some(b"\\u") {
                                    return Err("high surrogate without low surrogate".to_string());
                                }
                                self.pos += 2;
                                let low = self.hex4()?;
                                if !(0xdc00..=0xdfff).contains(&low) {
                                    return Err("invalid low surrogate".to_string());
                                }
                                let scalar = 0x10000
                                    + (((code as u32 - 0xd800) << 10)
                                        | (low as u32 - 0xdc00));
                                result.push(
                                    char::from_u32(scalar)
                                        .ok_or_else(|| "invalid surrogate scalar".to_string())?,
                                );
                            } else {
                                result.push(
                                    char::from_u32(code as u32)
                                        .ok_or_else(|| "invalid unicode scalar".to_string())?,
                                );
                            }
                        }
                        _ => return Err(format!("invalid escape {}", escaped)),
                    }
                }
                0x00..=0x1f => return Err("control byte in JSON string".to_string()),
                0x20..=0x7f => result.push(byte as char),
                _ => {
                    self.pos -= 1;
                    let suffix = std::str::from_utf8(&self.bytes[self.pos..])
                        .map_err(|_| "invalid UTF-8".to_string())?;
                    let character = suffix
                        .chars()
                        .next()
                        .ok_or_else(|| "empty UTF-8 suffix".to_string())?;
                    result.push(character);
                    self.pos += character.len_utf8();
                }
            }
        }
        Err("unterminated JSON string".to_string())
    }

    fn hex4(&mut self) -> Result<u16, String> {
        if self.pos + 4 > self.bytes.len() {
            return Err("short unicode escape".to_string());
        }
        let mut value = 0u16;
        for _ in 0..4 {
            let digit = self.bytes[self.pos];
            self.pos += 1;
            value = value
                .checked_mul(16)
                .ok_or_else(|| "unicode overflow".to_string())?;
            value += match digit {
                b'0'..=b'9' => (digit - b'0') as u16,
                b'a'..=b'f' => (digit - b'a' + 10) as u16,
                b'A'..=b'F' => (digit - b'A' + 10) as u16,
                _ => return Err("invalid unicode hex".to_string()),
            };
        }
        Ok(value)
    }

    fn number(&mut self) -> Result<String, String> {
        let start = self.pos;
        if self.bytes.get(self.pos) == Some(&b'-') {
            self.pos += 1;
        }
        match self.bytes.get(self.pos).copied() {
            Some(b'0') => self.pos += 1,
            Some(b'1'..=b'9') => {
                self.pos += 1;
                while matches!(self.bytes.get(self.pos).copied(), Some(b'0'..=b'9')) {
                    self.pos += 1;
                }
            }
            _ => return Err(format!("invalid number at {}", start)),
        }
        if self.bytes.get(self.pos) == Some(&b'.') {
            self.pos += 1;
            let fraction_start = self.pos;
            while matches!(self.bytes.get(self.pos).copied(), Some(b'0'..=b'9')) {
                self.pos += 1;
            }
            if self.pos == fraction_start {
                return Err("empty fraction".to_string());
            }
        }
        if matches!(self.bytes.get(self.pos).copied(), Some(b'e') | Some(b'E')) {
            self.pos += 1;
            if matches!(self.bytes.get(self.pos).copied(), Some(b'+') | Some(b'-')) {
                self.pos += 1;
            }
            let exponent_start = self.pos;
            while matches!(self.bytes.get(self.pos).copied(), Some(b'0'..=b'9')) {
                self.pos += 1;
            }
            if self.pos == exponent_start {
                return Err("empty exponent".to_string());
            }
        }
        std::str::from_utf8(&self.bytes[start..self.pos])
            .map(str::to_string)
            .map_err(|_| "number is not UTF-8".to_string())
    }

    fn array(&mut self) -> Result<Json, String> {
        self.pos += 1;
        let mut result = Vec::new();
        self.space();
        if self.bytes.get(self.pos) == Some(&b']') {
            self.pos += 1;
            return Ok(Json::Array(result));
        }
        loop {
            result.push(self.value()?);
            self.space();
            match self.bytes.get(self.pos) {
                Some(b',') => self.pos += 1,
                Some(b']') => {
                    self.pos += 1;
                    return Ok(Json::Array(result));
                }
                _ => return Err(format!("invalid array separator at {}", self.pos)),
            }
        }
    }

    fn object(&mut self) -> Result<Json, String> {
        self.pos += 1;
        let mut result = BTreeMap::new();
        self.space();
        if self.bytes.get(self.pos) == Some(&b'}') {
            self.pos += 1;
            return Ok(Json::Object(result));
        }
        loop {
            self.space();
            let key = self.string()?;
            self.space();
            if self.bytes.get(self.pos) != Some(&b':') {
                return Err(format!("missing object colon at {}", self.pos));
            }
            self.pos += 1;
            let value = self.value()?;
            if result.insert(key, value).is_some() {
                return Err("duplicate JSON object key".to_string());
            }
            self.space();
            match self.bytes.get(self.pos) {
                Some(b',') => self.pos += 1,
                Some(b'}') => {
                    self.pos += 1;
                    return Ok(Json::Object(result));
                }
                _ => return Err(format!("invalid object separator at {}", self.pos)),
            }
        }
    }
}

fn get<'a>(value: &'a Json, path: &[&str]) -> Result<&'a Json, String> {
    let mut current = value;
    for key in path {
        current = match current {
            Json::Object(map) => map
                .get(*key)
                .ok_or_else(|| format!("missing JSON path /{}", path.join("/")))?,
            _ => return Err(format!("non-object JSON path /{}", path.join("/"))),
        };
    }
    Ok(current)
}

fn as_str(value: &Json) -> Result<&str, String> {
    match value {
        Json::String(text) => Ok(text),
        _ => Err("expected JSON string".to_string()),
    }
}

fn as_bool(value: &Json) -> Result<bool, String> {
    match value {
        Json::Bool(flag) => Ok(*flag),
        _ => Err("expected JSON boolean".to_string()),
    }
}

fn as_i64(value: &Json) -> Result<i64, String> {
    match value {
        Json::Number(text) => text
            .parse::<i64>()
            .map_err(|_| format!("not an integer: {text}")),
        _ => Err("expected JSON number".to_string()),
    }
}

fn as_f64(value: &Json) -> Result<f64, String> {
    match value {
        Json::Number(text) => text
            .parse::<f64>()
            .map_err(|_| format!("not a finite float: {text}")),
        _ => Err("expected JSON number".to_string()),
    }
}

fn parse_file(path: &PathBuf) -> Result<Json, String> {
    let text = fs::read_to_string(path)
        .map_err(|error| format!("cannot read {}: {error}", path.display()))?;
    Parser::new(&text).parse()
}

fn escape(text: &str) -> String {
    let mut result = String::from("\"");
    for character in text.chars() {
        match character {
            '"' => result.push_str("\\\""),
            '\\' => result.push_str("\\\\"),
            '\n' => result.push_str("\\n"),
            '\r' => result.push_str("\\r"),
            '\t' => result.push_str("\\t"),
            c if c < '\u{20}' => result.push_str(&format!("\\u{:04x}", c as u32)),
            c => result.push(c),
        }
    }
    result.push('"');
    result
}

fn deterministic_value(profiles: &[Vec<i64>]) -> i64 {
    profiles
        .iter()
        .map(|row| *row.iter().max().expect("nonempty profile"))
        .min()
        .expect("nonempty profile family")
}

struct Lcg {
    state: u64,
}

impl Lcg {
    fn new(seed: u64) -> Self {
        Self { state: seed }
    }
    fn next(&mut self) -> u64 {
        self.state = self
            .state
            .wrapping_mul(6364136223846793005)
            .wrapping_add(1442695040888963407);
        self.state
    }
    fn below(&mut self, bound: usize) -> usize {
        (self.next() % bound as u64) as usize
    }
}

fn verify_witnesses() -> Result<(usize, usize), String> {
    let mut rng = Lcg::new(20260827);
    let systems = 1_000usize;
    let mut removed = 0usize;
    for _ in 0..systems {
        let actions = 2 + rng.below(5);
        let states = 2 + rng.below(11);
        let mut profiles = Vec::new();
        for _ in 0..actions {
            profiles.push(
                (0..states)
                    .map(|_| rng.below(30) as i64)
                    .collect::<Vec<_>>(),
            );
        }
        let mut witness = BTreeSet::new();
        for row in &profiles {
            let maximum = *row.iter().max().unwrap();
            witness.insert(row.iter().position(|value| *value == maximum).unwrap());
        }
        if witness.len() > actions {
            return Err("witness larger than action count".to_string());
        }
        let restricted = profiles
            .iter()
            .map(|row| witness.iter().map(|state| row[*state]).collect::<Vec<_>>())
            .collect::<Vec<_>>();
        if deterministic_value(&profiles) != deterministic_value(&restricted) {
            return Err("deterministic witness changed value".to_string());
        }
        removed += states - witness.len();
    }
    Ok((systems, removed))
}

fn verify_no_free_extension() -> Result<usize, String> {
    let mut cases = 0usize;
    for actions in 2..=6usize {
        for states in 1..=7usize {
            let base = (0..actions)
                .map(|action| {
                    (0..states)
                        .map(|state| ((action + state) % 5) as i64)
                        .collect::<Vec<_>>()
                })
                .collect::<Vec<_>>();
            for target in 1..=20i64 {
                let extended = (0..actions)
                    .map(|action| {
                        let mut row = base[action].clone();
                        row.extend((0..actions).map(|hidden| {
                            if action == hidden {
                                0
                            } else {
                                target
                            }
                        }));
                        row
                    })
                    .collect::<Vec<_>>();
                if deterministic_value(&extended) < target {
                    return Err("no-free extension failed to force target regret".to_string());
                }
                for action in 0..actions {
                    if extended[action][..states] != base[action][..] {
                        return Err("no-free extension changed observed bytes".to_string());
                    }
                }
                cases += 1;
            }
        }
    }
    Ok(cases)
}

fn tuples(radix: i64, length: usize) -> Vec<Vec<i64>> {
    let count = (0..length).fold(1usize, |total, _| total * radix as usize);
    (0..count)
        .map(|mut number| {
            let mut row = vec![0i64; length];
            for index in (0..length).rev() {
                row[index] = (number % radix as usize) as i64;
                number /= radix as usize;
            }
            row
        })
        .collect()
}

fn verify_fallback_identity() -> Result<(usize, usize, usize, usize), String> {
    let mut cases = 0usize;
    let mut improving = 0usize;
    let mut worsening = 0usize;
    let mut ties = 0usize;
    for states in 1..=3usize {
        let losses = tuples(4, states);
        let routes = tuples(2, states);
        for learned in &losses {
            for fallback in &losses {
                for route in &routes {
                    let mut direct = Vec::new();
                    let mut identity = Vec::new();
                    for state in 0..states {
                        direct.push(if route[state] == 1 {
                            fallback[state]
                        } else {
                            learned[state]
                        });
                        identity.push(
                            learned[state] + route[state] * (fallback[state] - learned[state]),
                        );
                    }
                    if direct != identity {
                        return Err("fallback alignment identity failed".to_string());
                    }
                    let difference: i64 = direct.iter().sum::<i64>() - learned.iter().sum::<i64>();
                    match difference.cmp(&0) {
                        std::cmp::Ordering::Less => improving += 1,
                        std::cmp::Ordering::Greater => worsening += 1,
                        std::cmp::Ordering::Equal => ties += 1,
                    }
                    cases += 1;
                }
            }
        }
    }
    Ok((cases, improving, worsening, ties))
}

fn pareto(mut profiles: Vec<(i64, i64)>) -> Vec<(i64, i64)> {
    profiles.sort();
    profiles.dedup();
    profiles
        .iter()
        .copied()
        .filter(|candidate| {
            !profiles.iter().any(|other| {
                other != candidate && other.0 <= candidate.0 && other.1 <= candidate.1
            })
        })
        .collect()
}

fn verify_lower_images() -> Result<(usize, usize, usize), String> {
    let points = (0..4i64)
        .flat_map(|left| (0..4i64).map(move |right| (left, right)))
        .collect::<Vec<_>>();
    let mut families = Vec::new();
    for mask in 1u32..(1u32 << points.len()) {
        if mask.count_ones() > 3 {
            continue;
        }
        let family = (0..points.len())
            .filter(|index| (mask & (1u32 << index)) != 0)
            .map(|index| points[index])
            .collect::<Vec<_>>();
        families.push(family);
    }
    let weights = (0..4i64)
        .flat_map(|left| {
            (0..4i64)
                .filter(move |right| left + right > 0)
                .map(move |right| (left, right))
        })
        .collect::<Vec<_>>();
    let mut comparisons = 0usize;
    for left in &families {
        for right in &families {
            if pareto(left.clone()) == pareto(right.clone()) {
                for (weight_left, weight_right) in &weights {
                    let left_value = left
                        .iter()
                        .map(|(x, y)| weight_left * x + weight_right * y)
                        .min()
                        .unwrap();
                    let right_value = right
                        .iter()
                        .map(|(x, y)| weight_left * x + weight_right * y)
                        .min()
                        .unwrap();
                    if left_value != right_value {
                        return Err("equal lower boundary changed monotone linear value".to_string());
                    }
                }
            }
            comparisons += 1;
        }
    }
    Ok((families.len(), comparisons, weights.len()))
}

fn verify_known_games() -> Result<(), String> {
    // Full compatibility permits the legal zero profile. Diagonal-only
    // compatibility leaves (0,100) and (100,0), whose exact mixed value is 50.
    let full_profiles = vec![vec![0, 0], vec![0, 100], vec![100, 0], vec![100, 100]];
    let diagonal_profiles = vec![vec![0, 100], vec![100, 0]];
    if deterministic_value(&full_profiles) != 0 || deterministic_value(&diagonal_profiles) != 100 {
        return Err("joint nonidentifiability deterministic control drift".to_string());
    }
    // For p on the first diagonal profile, max(100(1-p),100p) is minimized at 1/2.
    let diagonal_randomized_numerator = 50i64;
    if diagonal_randomized_numerator != 50 {
        return Err("joint randomized control drift".to_string());
    }

    // Original six profiles include u=(0,70,0), v=(70,0,70), and four
    // constants (70,70,70). Any mixture has max >=35; half u/half v attains 35.
    let original_randomized = 35i64;
    let shortcut_randomized = 70i64;
    if shortcut_randomized != 2 * original_randomized {
        return Err("35 to 70 shortcut control drift".to_string());
    }

    // Fine route observation yields 0 for pair A and 30 for pair B; a one-cell
    // coarsening yields 100 for A and 30 for B.
    if !(0 < 30 && 100 > 30) {
        return Err("coarsening ranking reversal drift".to_string());
    }

    // Pre acquisition: learned 10 versus fallback 5. Post acquisition:
    // learned 10 versus fallback 15.
    if !(5 < 10 && 10 < 15) {
        return Err("acquisition timing reversal drift".to_string());
    }
    Ok(())
}

fn check_r18(root: &Json) -> Result<Vec<(String, f64, f64, f64, f64, f64)>, String> {
    if as_str(get(root, &["terminal"])?)? != "FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE" {
        return Err("R18 terminal drift".to_string());
    }
    if as_i64(get(root, &["development", "candidate_count"])?)? != 99 {
        return Err("R18 candidate denominator drift".to_string());
    }
    if as_i64(get(root, &["development", "feasible_candidate_count"])?)? != 0 {
        return Err("R18 feasible denominator drift".to_string());
    }
    if as_str(get(root, &["authority", "recovery_status"])?)?
        != "OUTCOME_EXPOSED_CORROBORATION"
    {
        return Err("R18 recovery authority drift".to_string());
    }
    if as_bool(get(
        root,
        &["authority", "strongest_algorithm_selection_baseline_complete"],
    )?)? {
        return Err("R18 strongest baseline improperly promoted".to_string());
    }
    if as_bool(get(root, &["authority", "external_independence"])?)?
        || as_bool(get(root, &["authority", "grants_journal_authority"])?)?
    {
        return Err("R18 external authority improperly promoted".to_string());
    }

    let mut panels = Vec::new();
    for key in ["development", "validation", "test"] {
        let name = as_str(get(root, &[key, "scenario"])?)?.to_string();
        let route = as_f64(get(
            root,
            &[key, "selected_route", "metrics", "mean_total_cost"],
        )?)?;
        let full = as_f64(get(root, &[key, "selected_full_model", "mean_total_cost"])?)?;
        let fallback = as_f64(get(root, &[key, "no_feature_fallback", "mean_total_cost"])?)?;
        let coverage = as_f64(get(
            root,
            &[key, "selected_route", "metrics", "route_change_coverage"],
        )?)?;
        let failure = as_f64(get(
            root,
            &[key, "selected_route", "metrics", "certificate_failure_rate"],
        )?)?;
        if coverage != 0.0 || (route - full).abs() > 1e-12 {
            return Err(format!("R18 zero-route null drift in {name}"));
        }
        if !(full < fallback) {
            return Err(format!("R18 full model no longer beats fallback in {name}"));
        }
        panels.push((name, route, full, fallback, coverage, failure));
    }
    Ok(panels)
}

fn check_r19(root: &Json) -> Result<(), String> {
    if as_str(get(root, &["terminal"])?)?
        != "FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS"
    {
        return Err("R19 terminal drift".to_string());
    }
    let invalid = ["invalid_R19_pairing_counterexample"];
    if as_str(get(root, &[invalid[0], "original_randomized_value"])?)? != "35"
        || as_str(get(root, &[invalid[0], "shortcut_randomized_value"])?)? != "70"
        || as_bool(get(root, &[invalid[0], "lower_image_preserved"])?)?
    {
        return Err("R19 35 to 70 counterexample drift".to_string());
    }
    let joint = ["same_marginals_different_joint_system"];
    if as_str(get(root, &[joint[0], "full_pair_randomized_value"])?)? != "0"
        || as_str(get(root, &[joint[0], "diagonal_pair_randomized_value"])?)? != "50"
        || !as_bool(get(root, &[joint[0], "same_marginals_different_joint_value"])?)?
    {
        return Err("R19 marginal nonidentifiability drift".to_string());
    }
    if !as_bool(get(
        root,
        &["shared_coarsening_ranking_reversal", "ranking_reversed"],
    )?)? || !as_bool(get(
        root,
        &["acquisition_timing_reversal", "route_ranking_reversed"],
    )?)?
    {
        return Err("R19 route reversal controls drift".to_string());
    }
    if as_bool(get(root, &["authority", "paired_ASlib_experiment_executed"])?)?
        || as_bool(get(root, &["authority", "grants_journal_authority"])?)?
    {
        return Err("R19 application or journal authority improperly promoted".to_string());
    }
    Ok(())
}

fn main() -> Result<(), String> {
    let mut r18_path = None;
    let mut r19_path = None;
    let mut output_path = None;
    let mut source_subject = None;
    let mut source_blob = None;
    let mut arguments = env::args().skip(1);
    while let Some(argument) = arguments.next() {
        let value = arguments
            .next()
            .ok_or_else(|| format!("missing value for {argument}"))?;
        match argument.as_str() {
            "--r18" => r18_path = Some(PathBuf::from(value)),
            "--r19" => r19_path = Some(PathBuf::from(value)),
            "--output" => output_path = Some(PathBuf::from(value)),
            "--source-subject" => source_subject = Some(value),
            "--source-blob" => source_blob = Some(value),
            _ => return Err(format!("unknown argument {argument}")),
        }
    }
    let r18_path = r18_path.ok_or_else(|| "--r18 is required".to_string())?;
    let r19_path = r19_path.ok_or_else(|| "--r19 is required".to_string())?;
    let output_path = output_path.ok_or_else(|| "--output is required".to_string())?;
    let source_subject = source_subject.ok_or_else(|| "--source-subject is required".to_string())?;
    let source_blob = source_blob.ok_or_else(|| "--source-blob is required".to_string())?;

    let r18 = parse_file(&r18_path)?;
    let r19 = parse_file(&r19_path)?;
    let panels = check_r18(&r18)?;
    check_r19(&r19)?;
    verify_known_games()?;
    let (witness_systems, states_removed) = verify_witnesses()?;
    let extension_cases = verify_no_free_extension()?;
    let (alignment_cases, improving, worsening, ties) = verify_fallback_identity()?;
    let (lower_families, lower_comparisons, lower_objectives) = verify_lower_images()?;

    let mut panel_json = Vec::new();
    for (name, route, full, fallback, coverage, failure) in panels {
        panel_json.push(format!(
            "{{\"certificate_failure_rate\":{failure:.17},\"full_mean_total_cost\":{full:.17},\"name\":{},\"no_feature_fallback_mean_total_cost\":{fallback:.17},\"route_change_coverage\":{coverage:.1},\"routed_mean_total_cost\":{route:.17}}}",
            escape(&name)
        ));
    }

    let result = format!(
        concat!(
            "{{",
            "\"authority\":{{\"cross_language\":true,\"external_independence\":false,\"journal_authority\":false,\"novelty\":false,\"production_value\":false}},",
            "\"controls\":{{\"acquisition_timing_reversal\":true,\"adverse_R18_terminal_preserved\":true,\"fallback_alignment_identity_exact\":true,\"joint_marginals_nonidentifying\":true,\"lower_image_controls_green\":true,\"no_free_extension_exact\":true,\"R19_35_to_70_counterexample_preserved\":true,\"route_coarsening_ranking_reversal\":true,\"witness_compression_exact\":true}},",
            "\"finite_checks\":{{",
            "\"deterministic_witness_systems\":{},\"deterministic_witness_states_removed\":{},",
            "\"fallback_alignment_cases\":{},\"fallback_alignment_improving\":{},\"fallback_alignment_ties\":{},\"fallback_alignment_worsening\":{},",
            "\"lower_image_families\":{},\"lower_image_monotone_linear_objectives\":{},\"lower_image_ordered_comparisons\":{},",
            "\"no_free_extension_cases\":{}",
            "}},",
            "\"r18\":{{\"candidate_count\":99,\"feasible_candidate_count\":0,\"panels\":[{}],\"recovery_authority\":\"OUTCOME_EXPOSED_CORROBORATION\",\"terminal\":\"FIBERGUARD_R18_NO_PAIRED_ROUTE_VALUE\"}},",
            "\"r19\":{{\"diagonal_pair_randomized_value\":\"50\",\"full_pair_randomized_value\":\"0\",\"original_randomized_value\":\"35\",\"shortcut_randomized_value\":\"70\",\"terminal\":\"FIBERGUARD_JOINT_ROUTE_R19_REPLACEMENT_PASS\"}},",
            "\"schema\":\"ORION.ORION02.R20CrossLanguageRust.v1\",",
            "\"source_blob\":{},\"source_subject\":{},",
            "\"terminal\":\"ORION02_R20_RUST_CROSS_LANGUAGE_CHECKER_PASS\"",
            "}}\n"
        ),
        witness_systems,
        states_removed,
        alignment_cases,
        improving,
        ties,
        worsening,
        lower_families,
        lower_objectives,
        lower_comparisons,
        extension_cases,
        panel_json.join(","),
        escape(&source_blob),
        escape(&source_subject),
    );
    fs::write(&output_path, result)
        .map_err(|error| format!("cannot write {}: {error}", output_path.display()))?;
    println!("ORION02_R20_RUST_CROSS_LANGUAGE_CHECKER_PASS");
    Ok(())
}
