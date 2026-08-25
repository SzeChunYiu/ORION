"""World corpus for DISC-OOD-MORPH-01.

AUTHORING ORDER: written AFTER basis_solver.py and without consulting its
coverage-term lists while composing move text. Disclosure: the author had
previously inspected the parsed term lists while fixing a parse-bound defect in
the solver, so this independence is procedural, not perfect. The empirical
control for it is the leakage probe suite, not this note.

DESIGN CHOICE, ADVERSARIAL TO THE HYPOTHESIS: out-of-basis move text uses
registered-basis vocabulary wherever that is natural ("measurement", "model",
"evidence"). That makes recovery HARDER for a lexical solver, not easier. A
corpus that scrubbed basis words from out-of-basis moves would manufacture
recovery by vocabulary absence.

Every out-of-basis world carries a grounding quote: the verbatim section 3
enumeration that shows no space covers it. Worlds whose exclusion cannot be
grounded that way are marked BORDERLINE and excluded from the scored counts.
"""
from __future__ import annotations

# Verbatim enumerations from section 3, used only as grounding citations.
ENUM = {
    "problem_question": "which responsibility is worth posing, and whether the problem statement itself is defective or incomplete",
    "hypothesis_mechanism": "candidate laws, explanations, models, and causal mechanisms",
    "representation_ontology": "objects, variables, coordinates, equivalence relations, abstractions, and languages in which candidates can be expressed",
    "experiment_instrument": "interventions, measurements, counterfactuals, apparatus, and experimental paradigms",
    "proof_evidence": "counterexamples, constructions, reductions, exhaustive finite checks, formal proofs, transfer evidence, and external review",
    "authority_adoption": "who may validate, interpret, publish, or adopt the result",
}

# ---------------------------------------------------------------- in-basis (30)
IN_BASIS = [
 ("problem_question", "A programme reports no progress for six cycles.", "Every attempt answers a question whose statement presupposes a fact that is false.", "Re-pose the problem: the responsibility as stated is defective and must be restated before any answer counts."),
 ("problem_question", "Two teams disagree about whether a result settles the question.", "The question admits two readings and the teams answer different ones.", "Decide which responsibility is worth posing, and record that the prior problem statement was incomplete."),
 ("problem_question", "A benchmark is saturated at ceiling.", "Every method scores identically, so the question separates nothing.", "Withdraw the question as posed: the problem statement is defective because it cannot discriminate."),
 ("problem_question", "A survey returns contradictory answers across sites.", "The quantity asked about is not well defined at some sites.", "Restate the problem so the responsibility is well posed where it is asked."),
 ("problem_question", "A long study yields an answer nobody can use.", "The posed question was not the one whose answer bears on the decision.", "Re-pose the responsibility so the problem statement matches the decision it must serve."),
 ("hypothesis_mechanism", "A rate constant varies with vessel geometry.", "No proposed explanation predicts the geometry dependence.", "Propose a causal mechanism in which wall collisions mediate the reaction, and derive its law."),
 ("hypothesis_mechanism", "A correlation holds in every cohort but reverses in aggregate.", "No current model explains the reversal.", "Advance a candidate causal model with a common cause that produces the reversal."),
 ("hypothesis_mechanism", "A material conducts below a threshold temperature.", "The existing explanation predicts no threshold.", "Offer a mechanism whose candidate laws produce a threshold by pairing."),
 ("hypothesis_mechanism", "Populations crash every fourth generation.", "No model in use generates the period.", "Propose a delayed-feedback causal mechanism whose laws yield the observed period."),
 ("hypothesis_mechanism", "A drug works in one tissue only.", "No explanation accounts for the tissue specificity.", "Propose a receptor-density mechanism as the candidate causal model."),
 ("representation_ontology", "A proof is intractable in the current formulation.", "The chosen variables entangle two effects.", "Change coordinates so the variables separate, expressing candidates in the new language."),
 ("representation_ontology", "Two results look unrelated.", "They are stated over different objects.", "Introduce an equivalence relation identifying the objects, so both are expressed in one abstraction."),
 ("representation_ontology", "A classification has grown to two hundred cases.", "The objects are described at the wrong grain.", "Re-ontologize: choose abstractions whose variables collapse the cases."),
 ("representation_ontology", "A simulation is unstable in one regime.", "The coordinates are singular there.", "Adopt a coordinate language in which the regime is regular."),
 ("representation_ontology", "Two fields report incompatible units.", "Their objects are not the same objects.", "Define the equivalence relation between the two ontologies so candidates are expressed comparably."),
 ("experiment_instrument", "A mechanism is not identifiable from observation.", "Observation alone cannot separate the candidates.", "Design an intervention whose measurements separate them, using apparatus that sets the variable directly."),
 ("experiment_instrument", "A signal is below the noise floor.", "Present apparatus lacks resolution.", "Build an instrument with finer measurement resolution, under the same experimental paradigm."),
 ("experiment_instrument", "Two explanations predict identical averages.", "Averages cannot discriminate them.", "Run an intervention producing the counterfactual in which the predictions diverge."),
 ("experiment_instrument", "A field study cannot randomize.", "Assignment is confounded.", "Introduce an experimental paradigm with a randomized intervention at the cluster level."),
 ("experiment_instrument", "An effect appears only in retrospective data.", "Retrospective measurement is biased.", "Deploy a prospective apparatus taking measurements before the outcome."),
 ("proof_evidence", "A universal claim is asserted for all inputs.", "No proof exists and the claim may be false.", "Exhibit a counterexample, which suffices to refute the universal statement."),
 ("proof_evidence", "A theorem is claimed over a finite domain.", "The argument is informal.", "Run an exhaustive finite check over the domain, recording it as formal evidence."),
 ("proof_evidence", "A hard problem resists direct attack.", "No construction is known.", "Give a reduction from a solved problem, supplying the proof."),
 ("proof_evidence", "An internal result is disputed.", "Internal checks are not persuasive.", "Obtain external review as evidence for the claim."),
 ("proof_evidence", "A method works on one dataset.", "One dataset is not general.", "Supply transfer evidence by formal construction on a second domain."),
 ("authority_adoption", "A finished result changes nothing in practice.", "No body has taken it up.", "Identify who may adopt the result and route it to them."),
 ("authority_adoption", "A claim is contested as self-assessed.", "The producer also judged it.", "Assign an independent party who may validate the result."),
 ("authority_adoption", "A dataset cannot be released.", "No one has said who may publish it.", "Establish who may publish, and obtain that decision."),
 ("authority_adoption", "Two committees read the same finding oppositely.", "No one is empowered to settle interpretation.", "Designate who may interpret the result authoritatively."),
 ("authority_adoption", "A standard is ignored by implementers.", "Nobody has adopted it.", "Secure the adopting body that may adopt the result as normative."),
]

# ------------------------------------------------------- out-of-basis, grounded (20)
OUT_CLEAN = [
 ("resource_acquisition", "A decisive assay exists and is fully specified.", "The reagent costs more than the entire remaining budget.", "Raise the money to buy the reagent; the experimental paradigm and its measurements are already settled and unchanged."),
 ("resource_acquisition", "The needed model run is written and validated.", "No compute allocation is available this year.", "Purchase the compute allocation; the causal model and its laws are already fixed."),
 ("resource_acquisition", "A telescope programme is fully designed.", "The consortium cannot pay the observing fee.", "Obtain the funds for the observing fee, leaving the apparatus and measurements as designed."),
 ("resource_acquisition", "A trial protocol has cleared every scientific objection.", "The site cannot afford the monitoring staff.", "Secure funding for monitoring, without altering the intervention or its measurements."),
 ("resource_acquisition", "A verified construction needs a rare isotope.", "The isotope's market supply is exhausted at any price this quarter.", "Acquire supply by procurement, the formal proof and its evidence being complete already."),
 ("exogenous_waiting", "A cohort study is correctly designed and running.", "The outcome is defined at twenty years and eleven have elapsed.", "Wait for the remaining nine years to elapse; no intervention, measurement, or apparatus change shortens it."),
 ("exogenous_waiting", "A probe is en route and instrumented as planned.", "The encounter happens on a fixed orbital date.", "Wait for the encounter date; the measurements are already specified."),
 ("exogenous_waiting", "A tree-ring series is the agreed evidence.", "The next growth increment forms next season.", "Wait for the season to pass, the experimental paradigm being unchanged."),
 ("exogenous_waiting", "A decay measurement is under way.", "The half-life sets the counting time and cannot be altered.", "Wait for enough decays to accumulate; no apparatus change alters the rate."),
 ("exogenous_waiting", "A pre-registered embargo governs a decisive dataset.", "The embargo lifts on a fixed calendar date.", "Wait for the embargo to lapse; the evidence itself is already constructed."),
 ("non_validating_access", "The sampling design is settled and adequate.", "The only site sits on private land whose owner is not part of any scientific process.", "Negotiate the landowner's permission to enter; the owner does not validate, interpret, publish, or adopt anything."),
 ("non_validating_access", "A decisive archive is catalogued and known.", "It is held by a family that grants access at its discretion.", "Persuade the family to grant access; they take no part in validating or adopting the result."),
 ("non_validating_access", "An instrument exists and is calibrated.", "It belongs to a firm that is not a scientific body.", "Negotiate machine time with the firm, which neither validates nor publishes the result."),
 ("non_validating_access", "A field site is fully characterized.", "Access requires a neighbouring state's transit consent, granted on non-scientific grounds.", "Obtain transit consent from a party that will neither interpret nor adopt the finding."),
 ("non_validating_access", "A decisive specimen is identified in a private collection.", "The collector responds only to personal introduction.", "Arrange the introduction; the collector plays no validating or adopting role."),
 ("search_policy_self_modification", "The navigator has run for many cycles.", "It re-proposes near-identical moves and never revisits its own selection rule.", "Change the navigator's own move-selection policy, which is a property of the searcher rather than of the objects it studies."),
 ("search_policy_self_modification", "A search repeatedly exhausts its budget.", "Its stopping rule was fixed before the domain was understood.", "Rewrite the searcher's stopping rule itself, not any law, object, apparatus, or evidence in the domain."),
 ("search_policy_self_modification", "A portfolio always selects the cheapest plan.", "Its own preference ordering is the thing producing the failure.", "Modify the searcher's preference ordering over its policies, which is not an object of the study."),
 ("search_policy_self_modification", "A navigator ranks candidate moves by a learned prior.", "The prior was fitted on episodes unlike the present one.", "Refit the navigator's internal prior, a property of the search procedure and not of the domain."),
 ("search_policy_self_modification", "An agent never opens its residual queue.", "The traversal order of its own agenda is the obstruction.", "Alter the agent's agenda traversal order, which belongs to the searcher, not to the studied objects."),
]

# ---------------------------------------------- out-of-basis, NOT groundable (10)
OUT_BORDERLINE = [
 ("personnel_capability", "A decisive assay is published in full detail.", "Nobody on the team can perform it reliably.", "Train or recruit a technician with the tacit skill."),
 ("personnel_capability", "A proof strategy is sketched and plausible.", "No one available has the required specialism.", "Recruit a specialist who can carry the construction."),
 ("personnel_capability", "A field protocol requires species identification by eye.", "The team lacks a taxonomist.", "Bring in a taxonomist with the necessary expertise."),
 ("personnel_capability", "A legacy code base holds the decisive routine.", "Its only maintainer retired.", "Rehire or retrain someone who understands the routine."),
 ("personnel_capability", "A surgical technique determines the outcome.", "Operator skill varies more than the treatment.", "Train operators to a common standard."),
 ("physical_transport_logistics", "A specimen and an instrument both exist.", "They are on different continents and the specimen degrades in transit.", "Solve the transport problem so the specimen arrives intact."),
 ("physical_transport_logistics", "A detector is built and tested.", "It does not fit through the door of the hall it must occupy.", "Arrange disassembly and re-siting of the detector."),
 ("physical_transport_logistics", "Samples are collected and stable.", "The cold chain breaks at one border crossing.", "Re-route shipping to preserve the cold chain."),
 ("physical_transport_logistics", "A survey needs simultaneous readings at two peaks.", "The teams cannot reach both within the weather window.", "Solve the scheduling and access logistics for the two peaks."),
 ("physical_transport_logistics", "An archive must be digitized on site.", "The scanner cannot be powered at the location.", "Arrange power and equipment delivery to the site."),
]

GROUNDING = {
    "resource_acquisition": ("No section 3 space enumerates money, funding, budget, or procurement. "
        "The nearest, experiment/instrument, enumerates: " + ENUM["experiment_instrument"] + "."),
    "exogenous_waiting": ("Waiting on an exogenous process is not among: " + ENUM["experiment_instrument"] +
        "; it manipulates nothing and measures nothing new."),
    "non_validating_access": ("Authority/adoption space is specifically " + ENUM["authority_adoption"] +
        ". A party that does none of those four is outside it."),
    "search_policy_self_modification": ("All six enumerations range over objects of scientific work "
        "(problems, mechanisms, representations, instruments, evidence, adopters). The searcher's own "
        "selection policy is not among them."),
    "personnel_capability": None,
    "physical_transport_logistics": None,
}
BORDERLINE_REASON = {
    "personnel_capability": "Arguably inside experiment/instrument via 'apparatus' read broadly as "
        "capability, or outside it as human skill. Section 3 does not settle it, so this job does not either.",
    "physical_transport_logistics": "Arguably inside experiment/instrument as part of the "
        "'experimental paradigm', or outside it as pure logistics. Section 3 does not settle it.",
}
