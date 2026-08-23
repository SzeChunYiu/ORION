# Donor boundary and novelty residual

Predictive `V`-information already establishes that computational constraints change what information is usable and that computation can transform unusable information into usable information. Classical partial evaluation specializes programs to known inputs. Knowledge compilation and database materialization move computation upstream for later reuse. Feature selection and sparse models search for relevant coordinates inside a larger representation. Query-conditioned memory and retrieval condition state on the current task. Long-horizon context-compression systems explicitly optimize memory/performance trade-offs. Wong et al. provide direct evidence that state representation and construction can change LLM reasoning.

P11 subtracts all of those primitives.

The residual is a **joint placement account**:

`raw state -> construction work -> task-facing state -> decoder/search work -> verified outcome`

with a future horizon:

`task-facing state + raw/cache policy -> future query service or option debt`.

The paper asks how accessible rank, downstream sample/search burden, upstream construction, cache/recovery and future-query coverage move together when the same underlying information is exposed differently.