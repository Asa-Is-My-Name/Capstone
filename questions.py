"""
CODE CITATION
Based on: "How can I create multiple choice questions in Python?"
Published by: Gitnux Guides on March 20, 2023
Accessed on: May 3, 2023
URL: https://blog.gitnux.com/code/python-multiple-choice-questions/
"""

questions = [
    {
        "question": "Reduced ice leads to greater absorption of solar radiation.",
        "choices": ["True", "False"],
        "answer": "True"
    },
    {
        "question": "The lapse rate helps explain the role of latitude in impacting climate.",
        "choices": ["True", "False"],
        "answer": "False"
    },
    {
        "question": "Greenhouse gases absorb visible light from the Sun.",
        "choices": ["True", "False"],
        "answer": "False"
    },
    {
        "question": "Greenhouse gases absorb and re-radiate infrared radiation (heat energy).",
        "choices": ["True", "False"],
        "answer": "True"
    },
    {
        "question": "There has been more warming in the day than at night.",
        "choices": ["True", "False"],
        "answer": "False"
    },
    {
        "question": "Greenhouse gasses impact:",
        "choices": ["A. incoming solar radiation", "B. loss of infrared radiation",
                    "C. Both A and B", "D. None of the above"],
        "answer": "B"
    },
    {
        "question": "Compared to the amount of radiation received on the surface"
                    " of the earth by the Sun, about how much radiation does the"
                    " surface of the Earth receive reradiated back from greenhouse gases?",
        "choices": ["A. About 1/2 as much", "B. About 1/4 as much",
                    "C. An equal amount", "D. About twice as much"],
        "answer": "D"
    },
    {
        "question": "When does climate change occur?",
        "choices": ["A. When incoming and out going radiation are in balance",
                    "B. When in coming and out going radiation are not in balance",
                    "C. When there is consistently no incoming radiation",
                    "D. When there is consistently no outgoing radiation"],
        "answer": "B"
    },
    {
        "question": "Which process led to the removal of CO2 from the atmosphere in the Carboniferous period?",
        "choices": ["A. Chemosynthesis", "B. Respiration", "C. Carbon fusion", "D. Photosynthesis"],
        "answer": "D"
    },
    {
        "question": "Latent heat is involved in what processes?",
        "choices": ["A. Phase changes between ice, liquid water, and water vapor",
                    "B. Temperature changes", "C. Both A and B", "D. None of the above"],
        "answer": "A"
    },
    {
        "question": "Which of the following is a measure of the motion of particles contained in a substance?",
        "choices": ["A. Temperature", "B. Heat Energy", "C. Heat Flow",
                    "D. None of the above", "E. All of the above"],
        "answer": "A"
    },
    {
        "question": "Ocean temperatures are monitored by:",
        "choices": ["A. >3000 ARGO floats", "B. The ENSO monitoring system in the Pacific ocean",
                    "C. Satellites", "D. All of the above"],
        "answer": "D"
    },
    {
        "question": "What are common characteristics of El Nino and La Nina?",
        "choices": ["A. Changes in the tropical Pacific sea surface temperature",
                    "B. Significant shifts in climate throughout the globe",
                    "C. Both A and B", "D. None of the above"],
        "answer": "C"
    },
    {
        "question": "How do the conditions during La Nina phase of ENSO compare to those in the El Nino phase?",
        "choices": ["A. They are generally the same", "B. They are generally opposite",
                    "C. La Nina stores heat in the ocean while El Nino releases heat to the atmosphere",
                    "D. El Nino stores heat in the ocean while La Nina releases heat to the atmosphere",
                    "E. B and C are correct"],
        "answer": "E"
    },
    {
        "question": "When compared to Gyres in the Northern hemisphere, "
                    "what is the direction of gyres in the southern hemisphere?",
        "choices": ["A. Opposite", "B. The same", "C. Depends on the season",
                    "D. Depends on salinity", "E. A and D"],
        "answer": "A"
    },
    {
        "question": "Which of the following is true about the Oregon climate?",
        "choices": ["A. The water equivalent of snow in Bend is greater than that "
                    "of the total precipitation in the Willamette Valley",
                    "B. It rains very little in the summer because the land is generally warmer than the ocean",
                    "C. The coast is foggy in the summer because upwelling brings cold water to the surface",
                    "D. B and C", "E. A, B and C"],
        "answer": "D"
    },
    {
        "question": "Which do we know about precipitation?",
        "choices": ["A. It rains more when the air is warm",
                    "B. It rains more once the air has crossed a mountain pass",
                    "C. Hadley cells create more rain at the equator but deserts at 30 degrees N and S latitudes",
                    "D. A and C", "E. A, B and C"],
        "answer": "C"
    },
    {
        "question": "In what ways is heat circulated from the warm ocean to the cold poles?",
        "choices": ["A. Through Hadley cells and tornados", "B. Through the stratospheric O3 hole",
                    "C. Through ocean gyres and the great ocean conveyor belt", "D. A and C", "E. A, B and C"],
        "answer": "D"
    },
    {
        "question": "CO2 is higher now than:",
        "choices": ["A. The past 100 years",
                    "B. The past 10,000 years while humans have had agrarian life styles dependent on stable crops",
                    "C. The past 60,000 years", "D. The past 600,000 years during the coming and going of ice ages"],
        "answer": "D"
    },
    {
        "question": "What proportion of our CO2 emissions have ended up in the air compared to the oceans and land plants?",
        "choices": ["A. 100% in air and none to the oceans and land plants",
                    "B. 50% in air, 25% in the oceans, 25% in land plants",
                    "C. 75% in the air, 25% in the oceans, and none in land plants",
                    "D. 0% in the air or land plants – all the CO2 humans have emitted has been absorbed "
                    "by the oceans and is causing ocean acidification"],
        "answer": "D"
    },
    {
        "question": "Which of the following is true about greenhouse gases?",
        "choices": ["A. Water vapor is the most abundant greenhouse gas. However, evaporation into the atmosphere "
                    "cannot be controlled as it is just a physical process that follows air temperature",
                    "B. Humans currently emit greenhouse gases but do not take them h=out of the atmosphere",
                    "C. Natural ecosystems currently emit even more greenhouse gases than humans, "
                    "but also take them out of the atmosphere", "D. A and B", "E. A, B and C"],
        "answer": "E"
    },
    {
        "question": "How do we know whether the higher CO2 concentration were caused by humans?",
        "choices": ["A. The timing of our emissions is the same as the rise in CO2 concentrations as shown in ice core data",
                    "B. Tree rings show a decrease in 14C signatures reflective of the addition of the fossil fuel carbon to the atmosphere",
                    "C. Ice cores show a decrease in 13C signatures reflective of the addition of fossil fuel carbon to the atmosphere",
                    "D. A and B", "E. A, B and C"],
        "answer": "E"
    },
    {
        "question": "How does water vapor act to amplify effect of CO2 on warming the climate system without initiating it?",
        "choices": ["A. Water evaporates into the atmosphere as the climate warms",
                    "B. Water vapor rains out of the atmosphere within weeks of when it cools so has no long lasting impact",
                    "C. Water vapor follows the temperature changes rather than initiating them",
                    "D. All of the above"],
        "answer": "D"
    },
    {
        "question": "Which of the following can account for increased heat in the "
                    "Earth’s climate system that does not alter the air temperature?",
        "choices": ["A. Latent heat of vaporization", "B. Latent heat of ice melting",
                    "C. Absorption of heat energy into the ocean", "D. A and B", "E. A, B and C"],
        "answer": "D"
    },
    {
        "question": "Which provides more radiation to the Surface of the Earth?",
        "choices": ["A. The Sun", "B. Greenhouse Gases", "C. They are equal"],
        "answer": "B"
    },
]