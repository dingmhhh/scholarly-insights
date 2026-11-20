"""Sample data for Scholarly Insights.

All articles, authors and discussions below are fictional and exist only to
demonstrate the application. DOIs use the 10.5555 test prefix.
"""

CS, MED, ENV, ECO, PSY, EDU, PHY, SOC = (
    "Computer Science", "Medicine & Health", "Environmental Science", "Economics",
    "Psychology", "Education", "Physics", "Social Sciences",
)
RA, REV, META, CASE = "Research Article", "Review", "Meta-analysis", "Case Study"


def A(title, subject, type_, journal, year, authors, keywords, abstract, citations, oa):
    return dict(title=title, subject=subject, type=type_, journal=journal, year=year,
                authors=authors, keywords=keywords, abstract=abstract,
                citations=citations, open_access=oa)


ARTICLES = [
    A("Sparse Attention Mechanisms for Long-Document Retrieval", CS, RA,
      "Journal of Applied Computation", 2024,
      ["Mira Okonkwo", "Daniel Hartmann", "Li Wen"],
      ["attention", "information retrieval", "transformers", "efficiency"],
      "We introduce a block-sparse attention scheme that scales linearly with document length while preserving retrieval accuracy. "
      "Evaluated on four long-document benchmarks, the approach reduces memory use by 61% with less than 1% loss in recall.",
      142, True),
    A("A Survey of Federated Learning in Clinical Settings", MED, REV,
      "Digital Health Review", 2023,
      ["Priya Raman", "Tomás Beltrán"],
      ["federated learning", "privacy", "clinical data", "machine learning"],
      "Federated learning promises collaborative model training without centralising patient records. "
      "This review synthesises 87 studies, identifies recurring deployment barriers, and proposes a maturity framework for hospital adoption.",
      208, True),
    A("Carbon Sequestration Potential of Restored Coastal Wetlands", ENV, META,
      "Earth Systems Letters", 2022,
      ["Hannah Lindqvist", "Samuel Osei", "Rafaela Duarte"],
      ["carbon", "wetlands", "climate mitigation", "blue carbon"],
      "A meta-analysis of 143 restoration sites shows that coastal wetlands recover 70% of reference carbon stocks within 25 years. "
      "Salinity and sediment supply explain most of the observed variation.",
      317, True),
    A("Monetary Policy Transmission in Small Open Economies", ECO, RA,
      "Quarterly Review of Economic Studies", 2021,
      ["Andrei Volkov", "Chiamaka Eze"],
      ["monetary policy", "interest rates", "exchange rates", "inflation"],
      "Using a structural VAR on 22 small open economies, we show that exchange-rate pass-through weakens the interest-rate channel during periods of capital outflow. "
      "The results carry implications for inflation-targeting regimes.",
      96, False),
    A("Sleep Variability and Academic Performance in Adolescents", PSY, RA,
      "Journal of Developmental Psychology", 2023,
      ["Elena Moretti", "Jonah Weiss"],
      ["sleep", "adolescence", "academic performance", "longitudinal"],
      "In a three-year longitudinal cohort of 2,400 students, night-to-night sleep variability predicted lower grades independent of average sleep duration. "
      "Effects were strongest during exam periods.",
      121, True),
    A("Project-Based Learning and Student Engagement: Evidence from 40 Schools", EDU, CASE,
      "International Journal of Education Research", 2022,
      ["Grace Adeyemi", "Marcus Bell"],
      ["project-based learning", "engagement", "secondary education", "pedagogy"],
      "We report a multi-site case study of project-based learning adoption across forty secondary schools. "
      "Teacher professional development and shared planning time were the strongest predictors of sustained engagement gains.",
      74, False),
    A("Quantum Error Correction with Low-Overhead Surface Codes", PHY, RA,
      "Physical Review Advances", 2024,
      ["Kenji Watanabe", "Sofia Alvarez", "Henrik Dahl"],
      ["quantum computing", "error correction", "surface codes", "qubits"],
      "We present a modified surface-code layout that cuts physical-qubit overhead by roughly 35% at equal logical error rates. "
      "Numerical simulations under realistic noise models support the scheme's feasibility on near-term hardware.",
      188, False),
    A("Social Media Use and Civic Participation: A Cross-National Study", SOC, RA,
      "Journal of Social Inquiry", 2022,
      ["Nadia Haddad", "Oliver Grant"],
      ["social media", "civic engagement", "democracy", "cross-national"],
      "Drawing on survey data from 31 countries, we find that political content exposure on social platforms is associated with offline participation, but only where institutional trust is high. "
      "The relationship reverses in low-trust contexts.",
      163, True),
    A("Explainable AI for Credit Risk Assessment", CS, REV,
      "Journal of Applied Computation", 2023,
      ["Beatrice Nkemelu", "Rohan Mehta"],
      ["explainability", "credit risk", "machine learning", "fairness"],
      "Regulators increasingly require explanations for automated lending decisions. "
      "We compare post-hoc and inherently interpretable methods and discuss trade-offs between accuracy, stability and auditability.",
      109, True),
    A("Gut Microbiome Composition and Response to Immunotherapy", MED, META,
      "Clinical Oncology Insights", 2023,
      ["Yara Haddad", "Peter Lindgren", "Aiko Tanaka"],
      ["microbiome", "immunotherapy", "oncology", "biomarkers"],
      "Pooling 19 cohorts, we find that higher microbial diversity is associated with improved response to checkpoint inhibitors. "
      "Heterogeneity across sequencing protocols limits causal interpretation.",
      402, False),
    A("Urban Heat Islands and Green Infrastructure: A Global Review", ENV, REV,
      "Urban Ecology Reports", 2021,
      ["Carlos Mendoza", "Ingrid Solberg"],
      ["urban heat", "green infrastructure", "cities", "adaptation"],
      "Urban tree canopy and green roofs lower summer surface temperatures by 1–4°C in most climates. "
      "We review the evidence base and highlight gaps in the Global South.",
      256, True),
    A("Behavioural Nudges in Retirement Savings: A Field Experiment", ECO, RA,
      "Journal of Behavioural Economics", 2022,
      ["Tara Sullivan", "Jamal Washington"],
      ["nudges", "savings", "behavioural economics", "field experiment"],
      "In a randomised field experiment with 58,000 employees, a simple default-escalation prompt raised contribution rates by 1.9 percentage points. "
      "Effects persisted for at least 18 months.",
      134, False),
    A("Mindfulness Interventions for Workplace Burnout: A Meta-Analysis", PSY, META,
      "Applied Psychology Review", 2024,
      ["Leila Farouk", "Ben Carter"],
      ["mindfulness", "burnout", "workplace", "wellbeing"],
      "Across 62 randomised trials, mindfulness programmes yielded small-to-moderate reductions in emotional exhaustion. "
      "Benefits were larger for programmes combining individual practice with organisational change.",
      88, True),
    A("Adaptive Tutoring Systems and Mathematics Outcomes", EDU, RA,
      "Learning Technology Journal", 2023,
      ["Wei Zhang", "Amara Okafor"],
      ["adaptive learning", "mathematics", "tutoring", "edtech"],
      "A cluster-randomised trial in 120 classrooms shows that adaptive tutoring raises mathematics scores by 0.18 standard deviations. "
      "Gains were concentrated among initially low-achieving students.",
      97, True),
    A("Dark Matter Halo Profiles from Weak Lensing Surveys", PHY, RA,
      "Astrophysical Frontiers", 2021,
      ["Isabelle Fournier", "Rahul Kapoor"],
      ["dark matter", "weak lensing", "cosmology", "galaxies"],
      "We constrain the inner slope of dark matter halos using stacked weak-lensing signals from 1.2 million galaxies. "
      "The results disfavour strongly cuspy profiles at the 3σ level.",
      221, False),
    A("Remote Work and the Geography of Inequality", SOC, RA,
      "Journal of Social Inquiry", 2023,
      ["Fatima Idris", "Lukas Brandt"],
      ["remote work", "inequality", "regional development", "labour markets"],
      "Using administrative data from five countries, we show that the shift to remote work has widened wage gaps between metropolitan and rural workers. "
      "Housing-cost adjustments narrow but do not close the gap.",
      79, True),
    A("Graph Neural Networks for Drug–Target Interaction Prediction", CS, RA,
      "Computational Biology Letters", 2022,
      ["Anika Rao", "Stefan Novak"],
      ["graph neural networks", "drug discovery", "bioinformatics", "deep learning"],
      "We propose a heterogeneous graph architecture that integrates chemical structure, protein sequence and interaction networks. "
      "The model improves AUROC by 4.2% over strong baselines on three public benchmarks.",
      276, True),
    A("Telehealth Adoption During Public Health Emergencies: A Case Study", MED, CASE,
      "Digital Health Review", 2021,
      ["Marisol Vega", "Ahmed Siddiqui"],
      ["telehealth", "public health", "primary care", "access"],
      "This case study follows a regional health network's rapid telehealth rollout. "
      "We identify staffing, reimbursement and digital-literacy factors that shaped uptake across patient groups.",
      144, True),
    A("Microplastics in Freshwater Systems: Sources, Fate and Effects", ENV, REV,
      "Earth Systems Letters", 2023,
      ["Johanna Keller", "Tunde Bakare"],
      ["microplastics", "freshwater", "pollution", "ecotoxicology"],
      "We synthesise research on microplastic sources and transport in rivers and lakes. "
      "Evidence for sublethal effects on invertebrates is growing, while standardised sampling remains a major limitation.",
      190, True),
    A("Central Bank Digital Currencies and Financial Stability", ECO, REV,
      "Quarterly Review of Economic Studies", 2024,
      ["Viktor Petrenko", "Amelia Hayes"],
      ["CBDC", "financial stability", "banking", "payments"],
      "We review design choices for retail central bank digital currencies and their implications for bank funding and run risk. "
      "Holding limits and tiered remuneration emerge as the most discussed safeguards.",
      67, False),
    A("Social Support and Resilience After Major Life Transitions", PSY, RA,
      "Journal of Developmental Psychology", 2022,
      ["Camila Torres", "Ethan Wallace"],
      ["resilience", "social support", "life transitions", "wellbeing"],
      "A five-wave panel study of 3,100 adults shows that perceived social support buffers the psychological impact of job loss, relocation and bereavement. "
      "Quality of support mattered more than network size.",
      112, False),
    A("Peer Feedback in Higher Education Writing Courses", EDU, RA,
      "International Journal of Education Research", 2021,
      ["Hadiza Musa", "Oscar Lindholm"],
      ["peer feedback", "writing", "higher education", "assessment"],
      "In a quasi-experimental study across eight universities, structured peer feedback improved revision quality compared with instructor-only feedback. "
      "Students reported greater ownership of their writing.",
      58, True),
    A("Topological Phases in Photonic Lattices", PHY, RA,
      "Physical Review Advances", 2022,
      ["Mateo Rinaldi", "Yuki Sato"],
      ["photonics", "topological insulators", "lattices", "condensed matter"],
      "We demonstrate a robust edge-state transport in a two-dimensional photonic lattice with engineered disorder. "
      "The observed protection against backscattering agrees with tight-binding predictions.",
      149, False),
    A("Community Health Workers and Maternal Outcomes in Low-Resource Settings", MED, META,
      "Global Health Perspectives", 2022,
      ["Esther Mwangi", "Pavel Kovář", "Divya Nair"],
      ["community health workers", "maternal health", "global health", "intervention"],
      "A meta-analysis of 48 trials finds that community health worker programmes reduce neonatal mortality by 17%. "
      "Training intensity and supervision frequency moderate the effect.",
      339, True),
    A("Privacy-Preserving Analytics with Differential Privacy: Practical Guidelines", CS, REV,
      "Journal of Applied Computation", 2022,
      ["Oluwaseun Adeleke", "Clara Jensen"],
      ["differential privacy", "data analytics", "privacy", "security"],
      "Differential privacy is moving from theory to deployment. "
      "We distil practical guidelines on privacy-budget allocation, utility measurement and communication of guarantees to non-technical stakeholders.",
      173, True),
    A("Migration, Language and Identity in Second-Generation Youth", SOC, CASE,
      "Journal of Social Inquiry", 2021,
      ["Samira Qureshi", "Tomas Eriksen"],
      ["migration", "identity", "language", "youth"],
      "Through 60 in-depth interviews, this case study explores how second-generation youth navigate multilingual identities across home, school and online spaces. "
      "Findings point to fluid, context-dependent belonging.",
      52, False),
    A("Machine Learning Forecasts of Regional Electricity Demand", CS, RA,
      "Energy Informatics", 2023,
      ["Ravi Shankar", "Ingeborg Haugen"],
      ["forecasting", "energy", "machine learning", "time series"],
      "We compare gradient boosting, recurrent networks and hybrid statistical models for day-ahead electricity demand across 14 regions. "
      "Hybrid approaches deliver the most stable accuracy during extreme weather events.",
      101, True),
    A("Ocean Acidification and Coral Reef Calcification Rates", ENV, RA,
      "Marine Science Quarterly", 2024,
      ["Leilani Kahale", "Dmitri Ivanov"],
      ["ocean acidification", "coral reefs", "calcification", "climate change"],
      "Long-term mesocosm experiments show that calcification declines non-linearly once aragonite saturation drops below a critical threshold. "
      "Heat-tolerant coral genotypes partially offset the decline.",
      64, True),
    A("Universal Basic Income Pilots: What Do the Data Say?", ECO, META,
      "Journal of Behavioural Economics", 2024,
      ["Greta Lund", "Kwame Asante"],
      ["basic income", "labour supply", "poverty", "welfare"],
      "We pool results from 27 pilot programmes and find negligible effects on labour supply alongside improvements in wellbeing and financial security. "
      "Programme duration is a key moderator.",
      131, True),
    A("Digital Literacy Gaps Among Older Adults: Barriers and Interventions", EDU, REV,
      "Learning Technology Journal", 2022,
      ["Rosalind Park", "Emeka Obi"],
      ["digital literacy", "older adults", "adult education", "inclusion"],
      "This review examines barriers that limit older adults' use of digital services and evaluates intervention formats. "
      "Peer-led, hands-on programmes outperform lecture-based instruction.",
      83, True),
    A("Cognitive Load and Decision Fatigue in Clinical Triage", PSY, CASE,
      "Applied Psychology Review", 2023,
      ["Nikolai Orlov", "Hana Suzuki"],
      ["cognitive load", "decision making", "triage", "healthcare"],
      "Observational data from three emergency departments show that triage accuracy declines late in extended shifts. "
      "Structured decision aids mitigated the effect without slowing throughput.",
      70, False),
]

CATEGORIES = [
    ("general", "General Discussion", "Open conversation about research life and the platform."),
    ("methods", "Methods & Statistics", "Study design, analysis choices and reproducibility."),
    ("reading-group", "Reading Group", "Discuss specific articles with other readers."),
    ("careers", "Careers & Publishing", "Peer review, funding, and academic careers."),
]

# (title, body, author, category, article_index or None, votes, [(author, body, votes), ...])
THREADS = [
    ("How do you evaluate sparse attention claims on long documents?",
     "The block-sparse attention paper reports a 61% memory reduction. I'd like to reproduce this on our own corpus.\n\nWhich baselines and benchmarks do you think are fair for comparison, and how do you control for hardware differences?",
     "Dana Whitfield", "reading-group", 0, 14,
     [("Mira Okonkwo", "Thanks for the interest! Our configuration files are in the supplementary material. I'd also compare against a sliding-window baseline with matched memory.", 9),
      ("Jun Park", "Report wall-clock as well as peak memory. Memory savings do not always translate into speed on older accelerators.", 5)]),
    ("Preregistration: worth it for exploratory work?",
     "I'm designing an exploratory study and my supervisor is pushing for preregistration. Does it make sense when the hypotheses are not yet well formed?",
     "Ines Carvalho", "methods", None, 21,
     [("Prof. T. Nwosu", "Yes, but register your analysis plan and label which analyses are confirmatory versus exploratory. Transparency is the point, not rigidity.", 12),
      ("Alex Rivera", "Registered reports are also worth a look. The journal commits to publish based on the question and method, not the result.", 8),
      ("Ines Carvalho", "That's helpful, thank you both. I'll draft a two-tier plan.", 2)]),
    ("Heterogeneity in microbiome meta-analyses",
     "The immunotherapy meta-analysis notes heterogeneity across sequencing protocols. How would you handle that in a re-analysis?",
     "Sam Okafor", "reading-group", 9, 7,
     [("Yara Haddad", "Mixed-effects models with protocol as a random effect helped, and we ran a leave-one-cohort-out sensitivity check.", 6)]),
    ("Tips for responding to a harsh reviewer comment",
     "Got a very blunt Reviewer 2 comment on my first submission. Any advice on responding constructively without sounding defensive?",
     "Priyanka Das", "careers", None, 33,
     [("Marcus Bell", "Thank them, address the substance point by point, and make changes where you can. Briefly and politely explain where you disagree.", 19),
      ("Hannah Lindqvist", "Wait a couple of days before writing the reply. Your first draft is rarely the one to send.", 14)]),
    ("Welcome to the Scholarly Insights community!",
     "This forum is a place to discuss articles, methods and the practice of research. Please keep discussion respectful, cite sources where possible and stay on topic.\n\nIntroduce yourself below!",
     "Scholarly Insights Team", "general", None, 18, []),
    ("Open access vs. subscription: how do you decide where to publish?",
     "Our funder now requires open access but many of the best journals in my niche are subscription-based. What are your strategies?",
     "Lars Eklund", "careers", None, 11,
     [("Esther Mwangi", "Check for green open access: many journals allow a preprint or accepted manuscript in a repository after an embargo.", 7)]),
]
