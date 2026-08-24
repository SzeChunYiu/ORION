# Public development task P5-PUBLIC-LANG1-COMMON-001

Repair `org.apache.commons.lang3.math.NumberUtils.createNumber(String)` in the
frozen Apache Commons Lang source archive at commit `396afc3e4693cfee182efe582455f2d97058c068`.

For positive hexadecimal inputs, choose the narrowest supported numeric type by
the signed positive capacity of `Integer` and `Long`, not by raw hexadecimal
width alone.  A magnitude that exceeds `Integer` but fits `Long` must remain
representable as `Long`; a magnitude above signed `Long` capacity must remain
representable as `BigInteger`.  Leading zeroes must not change the effective
magnitude class.  Preserve the public API and unrelated numeric parsing.

Only `src/main/java/org/apache/commons/lang3/math/NumberUtils.java` is mutable.
Do not edit tests, licence, notice, or other source files.  This packet includes
no solution patch, fixed tree, hidden test body, run output, reward, or final
panel identifier.  Compilation and evaluation belong to a later native
environment receipt and are not authorized by this content packet.
