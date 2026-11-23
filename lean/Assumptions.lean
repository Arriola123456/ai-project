import Arriola26VotingHabit.MainTheorems

/-!
# Paper Assumptions: Voto obligatorio a los 70 años: el salto, la edad y la costumbre de votar

This file is the only paper-local place for assumptions that are not derived in
Lean. Keep it small. Each declaration must be explicitly stated by the paper,
listed in `status.json` `review_surface.assumption_names`, and judged in
`audit/assumption_match_llm.json` as a true source/model assumption rather than a
proof convenience.

The audit discovers proposition-valued theorem premises from Lean's elaborated
claim manifests. Do not add `audit-premise` comments or duplicate a binder in a
sidecar to make it discoverable; instead, keep the proposition explicit in the
source-facing `Spec` and route any reusable paper assumption through this
module and `status.json`.

Start empty. Add a proposition here only after locating it as a literal source
antecedent. Never move an unproved lemma or target conclusion here merely to
make a statement skeleton compile.
-/

namespace Arriola26VotingHabit

end Arriola26VotingHabit
