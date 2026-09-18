/**
 * Curated academic presets.
 *
 * Each preset is deliberately dense, polysyllabic and qualification-heavy so
 * that the demo can show the transformation working on the exact kind of text
 * that defeats neurodivergent readers in higher education.
 */

export interface SampleDocument {
  id: string;
  title: string;
  subject: string;
  description: string;
  text: string;
}

export const SAMPLE_DOCUMENTS: SampleDocument[] = [
  {
    id: 'economics',
    title: 'Game Theory & Nash Equilibrium',
    subject: 'Economics',
    description: 'Mixed-strategy equilibria, trembling-hand perfection and empirical limits.',
    text: `In finite non-cooperative games, Nash's existence theorem guarantees that every game with a finite set of players and a finite set of pure strategies admits at least one equilibrium, possibly in mixed strategies. Yet the predictive value of this result remains contested, because multiplicity of equilibria means the theory frequently fails to specify which outcome will actually obtain. Refinements such as Selten's trembling-hand perfection and Kohlberg and Mertens' stability criterion were introduced precisely to prune implausible equilibria, but no refinement enjoys universal acceptance.

Consider the canonical ultimatum game. Subgame-perfect equilibrium predicts that the proposer offers the smallest possible positive amount and the responder accepts it, because rejection yields zero. Experimental evidence undermines this prediction systematically: responders routinely reject offers below approximately thirty percent of the stake, thereby incurring a personal cost to punish unfairness. This divergence is not a laboratory artefact; it replicates across dozens of industrialised and small-scale societies, although rejection thresholds vary with market integration and anonymity.

The tension between equilibrium prediction and observed behaviour has methodological consequences. Payoff-monotonicity, an innocuous-seeming assumption, is violated by several refinements, and the assumption of common knowledge of rationality is empirically fragile. Consequently, applied economists increasingly treat Nash equilibrium as a consistency requirement on beliefs rather than as a behavioural prediction, embedding it within models that specify bounded rationality, learning dynamics, or social preferences. The caveat matters for policy: a mechanism designed around equilibrium assumptions may fail catastrophically when agents deviate systematically, and the direction of the failure is often not inferable from the model itself.`,
  },
  {
    id: 'neuroscience',
    title: 'Working Memory & the Prefrontal Cortex',
    subject: 'Neuroscience',
    description: 'Capacity limits, dopaminergic modulation and the ADHD evidence base.',
    text: `Working memory refers to the limited-capacity system that temporarily maintains and manipulates information in the service of ongoing cognition. Baddeley and Hitch's multicomponent model distinguishes a phonological loop, a visuospatial sketchpad, an episodic buffer, and a central executive, though contemporary accounts increasingly treat these as functionally dissociable rather than anatomically discrete modules. Capacity estimates in healthy adults converge on approximately four plus or minus one chunks, substantially lower than the classical seven-item claim, and capacity declines monotonically across the adult lifespan.

Persistent activity in dorsolateral prefrontal cortex has long been interpreted as the neural substrate of maintenance. However, single-unit recordings in non-human primates indicate that stimulus-selective activity is sparse and dynamic, and that much of the apparently persistent signal may reflect short-lived activity sampled at successive time points rather than a stable attractor. This distinction matters because it weakens the inference from fMRI activation to a dedicated storage buffer.

Dopaminergic signalling modulates the signal-to-noise ratio of prefrontal representations, following an inverted-U function: moderate D1 receptor stimulation improves stability, whereas excessive or insufficient stimulation degrades it. The inverted-U provides the leading mechanistic account of working memory deficits in ADHD, yet the evidence is qualified in important respects. Effect sizes for working memory impairments in ADHD are moderate and heterogeneous, a substantial minority of diagnosed individuals perform within the normal range, and training studies reliably improve trained tasks while showing limited transfer to untrained measures of academic attainment. Reviewers therefore caution against treating working memory training as a substitute for instructional accommodation.`,
  },
  {
    id: 'legal',
    title: 'Legal Interpretation & the Rule of Recognition',
    subject: 'Legal Philosophy',
    description: 'Hart-Devlin debate, penumbral meaning and defeasibility of rules.',
    text: `Hart's concept of law rests on the union of primary rules of obligation and secondary rules of recognition, change, and adjudication. The rule of recognition is not itself a valid legal rule but a social practice: officials converge on criteria of validity, and that convergence explains the systematic character of a legal order without positing a sovereign command. Critics, most notably Dworkin, argue that this account cannot explain hard cases, in which judges reason from principles rather than from pedigree criteria, and that the resulting theory is a model of rules rather than of law.

The debate turns partly on the semantics of penumbral meaning. Hart maintains that general terms have a core of settled application and a penumbra of uncertainty, and that in the penumbra judges exercise constrained discretion. Dworkin denies that discretion so understood is compatible with the requirement that legal obligations be grounded in pre-existing standards rather than in judicial choice. Subsequent work has attempted to reconcile the positions by distinguishing theoretical from practical disagreement and by specifying the conditions under which a rule is defeasible, that is, defeated by competing considerations it does not itself enumerate.

Two caveats deserve emphasis. First, the rule of recognition thesis is a claim about the existence conditions of a legal system, not a claim about how judges ought to decide particular cases; conflating the two generates a large volume of avoidable dispute. Second, defeasibility is not equivalent to indeterminacy. A rule may be defeated in a specific case while remaining determinate in its core application, and much of the critical literature elides this distinction, producing scepticism that is broader than the premises licensed.`,
  },
];
