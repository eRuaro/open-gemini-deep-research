Okay, here's a comprehensive research report on Group Relative Policy Optimization (GRPO) for equitable technical report generation, designed to be engaging and informative:

**Title: Leveling the Playing Field: How Group Relative Policy Optimization Can Build Fairer AI for Technical Report Generation**

**Executive Summary: The Algorithmic Mirror and the Quest for Equity**

Artificial intelligence (AI), and specifically Large Language Models (LLMs), are increasingly used to automate tasks like technical report generation.  Like a powerful mirror, these systems reflect the data they are trained on. If that data contains societal biases – and it almost certainly does – the AI will amplify those biases, leading to inequitable outcomes. This report explores a promising approach: *Group Relative Policy Optimization (GRPO)*, and its variants, as a method to build fairer AI systems for technical report generation.

We delve into the core problem: how can we ensure that AI-generated technical reports are fair and equitable across different groups (defined by race, gender, socioeconomic status, etc.)? We examine traditional AI training methods, like Proximal Policy Optimization (PPO), and then introduce GRPO as a novel solution that directly addresses group-level disparities. GRPO works by comparing the quality of *groups* of AI-generated reports relative to each other, rather than relying on a single, potentially biased, "absolute" reward signal. We also explore Hybrid GRPO, which combines the strengths of PPO and GRPO.

This report is not just a technical deep-dive. It's a journey that explores:

*   **The Human Impact:** How biased AI can perpetuate real-world inequalities.
*   **The Technical Solution:** The mechanics of GRPO and how it promotes fairness.
*   **The Practical Steps:** How to implement GRPO, analyze data for bias, and generate equitable reports.
*   **The Future Landscape:** The potential of GRPO to revolutionize AI fairness beyond report generation.

Our key conclusion is that GRPO, and related techniques like Subgroup Threshold Optimization (STO) and causal inference methods, offer a powerful toolkit for building more equitable AI systems. By consciously addressing group-level fairness, we can move towards an AI future that benefits everyone, not just a privileged few. This requires a multi-faceted approach, combining technological innovation with a deep understanding of social equity and responsible data practices.

---

**Part 1: The Uneven Playing Field – Bias in AI-Generated Reports**

**1.1 The "Day in the Life" of Biased Reporting**

Imagine two equally qualified engineers, Anya and Ben, applying for a promotion.  Their performance reviews, including technical reports they've authored, are analyzed by an AI system.  Unbeknownst to anyone, the AI has been trained on data that subtly favors reports written in a style more common among men.  Anya's reports, while technically sound and insightful, are consistently rated lower than Ben's, even if their actual contributions are equal.  Anya is denied the promotion, not because of her skills, but because of an invisible, algorithmic bias.

This "day in the life" scenario illustrates the potential harm of biased AI in a seemingly objective task like technical report evaluation. The bias isn't necessarily malicious; it's often a subtle reflection of historical inequities embedded in the training data.

**1.2 The Roots of Bias: Data, Algorithms, and Society**

The problem of AI bias is multi-layered:

*   **Data Bias:** Training data often overrepresents certain demographics and underrepresents others. For example, a dataset of technical reports might contain more reports written by men than women, or more reports from specific geographic regions or institutions. This imbalance skews the AI's perception of what constitutes a "good" report. (Brookings.edu, NIH.gov)
*   **Algorithmic Bias:** Even with balanced data, the algorithms themselves can introduce bias. Traditional reinforcement learning algorithms, like PPO, optimize for a single reward function. If this reward function is not carefully designed to account for group fairness, it can lead to disparate outcomes. (Arxiv.org)
*   **Societal Bias:** AI systems don't exist in a vacuum. They are developed and deployed within a society that already grapples with systemic inequalities. These societal biases inevitably seep into the data and the design choices made by AI developers. (Soroptimistinternational.org, Bridgespan.org)

**1.3 The Specific Challenge: Equitable Technical Report Generation**

In the context of technical report generation, bias can manifest in several ways:

*   **Content Bias:** The AI might favor certain topics, writing styles, or technical approaches that are more common within a particular group.
*   **Evaluation Bias:** The AI might use metrics that are implicitly biased, such as favoring longer reports, more complex sentence structures, or specific jargon.
*   **Access Bias:** The AI might be trained on data that is not equally accessible to all groups. For example, if the AI is trained primarily on reports from top-tier universities, it might disadvantage individuals from less prestigious institutions.

**1.4 Why Traditional Solutions Fall Short**

Standard AI training methods, including Proximal Policy Optimization (PPO), are powerful but often insufficient for addressing group fairness. PPO is a foundational deep reinforcement learning algorithm that optimizes a policy (the AI's decision-making process) by iteratively improving it within a "trust region" to ensure stable learning. (Arxiv.org) While PPO is efficient and effective, it primarily focuses on maximizing overall performance, not on ensuring equitable outcomes across different groups. It relies on a single reward function, which, as discussed, can be a source of bias.

---

**Part 2: GRPO – A New Paradigm for Fairness**

**2.1 Introducing Group Relative Policy Optimization (GRPO)**

GRPO offers a fundamentally different approach to policy optimization. Instead of relying on an absolute reward signal, GRPO focuses on *relative* comparisons between *groups* of AI-generated outputs. (Arxiv.org, Medium.com)

**Here's the core idea:**

1.  **Generate Multiple Responses:** For a given input (e.g., a set of data to be summarized in a technical report), the AI generates *multiple* candidate reports.
2.  **Group the Responses:** These responses are grouped together. The size and composition of these groups are crucial design choices, which we'll discuss later.
3.  **Relative Evaluation:** Within each group, the reports are compared *to each other*. The AI learns to identify which reports are *relatively better* within the group, even if none of them are perfect. This eliminates the need for an external, potentially biased, evaluator.
4.  **Reinforce Improvements:** The AI is rewarded for generating reports that are consistently ranked higher *within their group*. This encourages the AI to explore a wider range of styles and approaches, rather than converging on a single, potentially biased, "optimal" solution.

**2.2 The Power of Relative Comparisons: An Analogy**

Imagine judging a baking competition. Instead of giving each cake an absolute score (e.g., 8/10), you compare the cakes *to each other*. You might say, "This cake is moister than that one," or "This cake has a better flavor balance." This relative judgment is less susceptible to individual biases (e.g., a judge who prefers very sweet cakes) because it focuses on the differences *within* the group. GRPO applies a similar principle to AI training.

**2.3 Hybrid GRPO: Combining the Best of Both Worlds**

Hybrid GRPO builds upon both PPO and GRPO. It leverages the stability and efficiency of PPO's value function-based learning while incorporating GRPO's relative comparisons. (Arxiv.org) A key addition is *empirical multi-sample action evaluation*. This means that the AI doesn't just evaluate a single report at a time; it evaluates multiple reports simultaneously, further enhancing the robustness of the learning process.

**2.4 The GRPO Algorithm: A Technical Deep Dive (Simplified)**

While a full mathematical treatment is beyond the scope of this report, here's a simplified overview of the GRPO algorithm:

*   **Loss Function:** GRPO uses a modified loss function that encourages the AI to maximize the probability of generating reports that are ranked higher within their group. This loss function is based on the relative rankings, not on absolute scores.
*   **Policy Updates:** The AI's policy is updated iteratively, just like in PPO, but the updates are guided by the GRPO loss function, which emphasizes relative improvements.
*   **Group Formation:** The way groups are formed is a critical parameter. Groups can be formed randomly, or they can be based on specific criteria (e.g., grouping reports that address similar topics or use similar data sources).

**2.5 Advantages of GRPO for Equitable Report Generation**

*   **Reduced Reliance on Biased Reward Functions:** GRPO's relative comparisons minimize the impact of biases that might be embedded in a single reward function.
*   **Enhanced Exploration:** GRPO encourages the AI to explore a wider range of report styles and content, leading to more diverse and potentially more equitable outputs.
*   **Improved Robustness:** GRPO's focus on relative improvements makes it less sensitive to noise and outliers in the training data.
*   **Scalability:** GRPO simplifies reward estimation, making training faster and more scalable, especially for complex tasks like technical report generation. (Medium.com)

---

**Part 3: Implementing Equitable Report Generation with GRPO**

**3.1 Defining "Equitable" and "Groups"**

Before implementing GRPO, we need to define precisely what we mean by "equitable" and how we will define the "groups" for relative comparison. This is a crucial step that requires careful consideration of the specific context and potential sources of bias.

*   **Defining Equitable Outcomes:** Equitable technical report generation means ensuring that the AI's output does not systematically disadvantage any particular group. This could manifest as:
    *   **Equal Opportunity:** Ensuring that reports from different groups have an equal chance of being rated highly, assuming equal underlying quality.
    *   **Equal Representation:** Ensuring that the AI generates reports that reflect the diversity of perspectives and experiences of different groups.
    *   **Equal Impact:** Ensuring that the use of AI-generated reports does not exacerbate existing inequalities.

*   **Defining Groups:** Groups can be defined based on various demographic factors, including:
    *   **Race/Ethnicity:** Ensuring fairness across different racial and ethnic groups. (Bridgespan.org, NIH.gov)
    *   **Gender:** Ensuring fairness between men, women, and non-binary individuals. (Bridgespan.org, NIH.gov)
    *   **Socioeconomic Status:** Ensuring fairness across different income levels and educational backgrounds.
    *   **Location:** Ensuring fairness across different geographic regions. (Bridgespan.org)
    *   **Age:** Ensuring fairness across different age groups. (Bridgespan.org, NIH.gov)
    *   **Disability Status:** Ensuring fairness for individuals with disabilities. (NIH.gov)

    The choice of groups will depend on the specific application and the potential sources of bias. It's crucial to conduct a thorough analysis of the data and the context to identify the most relevant groups.

**3.2 Data Analysis and Disaggregation**

Data disaggregation is essential for identifying and mitigating bias. This involves breaking down data by demographic groups to reveal disparities that might be hidden in aggregate statistics. (Bridgespan.org)

*   **Data Collection:** Ensure that data collection processes are inclusive and representative of all relevant groups.
*   **Data Labeling:** If the data requires labeling (e.g., rating the quality of reports), ensure that the labeling process is free from bias.
*   **Data Analysis Techniques:** Use a variety of data analysis techniques to identify potential biases, including:
    *   **Descriptive Statistics:** Calculate basic statistics (mean, median, standard deviation) for each group to identify differences in distributions. (MLR.Press)
    *   **Comparative Analysis:** Use techniques like difference-in-differences, regression, and correlation analysis to compare outcomes across groups. (MLR.Press)
    *   **Visualization:** Use charts and graphs (bar charts, line charts, scatter plots, maps) to visualize data and identify patterns of bias. (MLR.Press)
    *   **Statistical Significance Testing:** Use statistical tests to determine whether observed differences between groups are statistically significant. (MLR.Press)

**3.3 Technical Report Structure for GRPO Optimization**

When generating technical reports about GRPO, a clear and structured format is essential. Here's a recommended structure:

1.  **Problem Definition:** Clearly state the problem being addressed (e.g., bias in AI-generated technical reports) and the specific groups that are being considered. (Medium.com)
2.  **Algorithm Description:** Provide a detailed description of the GRPO algorithm, including the loss function, policy update mechanism, and group formation strategy. (Medium.com)
3.  **Experimental Setup:** Describe the environment in which the algorithm was tested, including the data used, the evaluation metrics, and any hyperparameters. (Medium.com)
4.  **Results:** Present the results of the experiments, including learning curves, quantitative metrics (e.g., fairness metrics), and qualitative examples of generated reports. (Medium.com)
5.  **Error Analysis:** Analyze the errors made by the algorithm and identify potential sources of remaining bias. (Medium.com)
6.  **Conclusion:** Summarize the findings and discuss the implications for equitable AI development. (Medium.com)

**3.4 Subgroup Threshold Optimization (STO)**

STO is a complementary technique that can be used in conjunction with GRPO. STO focuses on optimizing the *classification thresholds* for individual subgroups. (FACCTConference.org)

*   **The Problem:** In many AI applications, a decision is made based on a score (e.g., classifying a report as "high quality" or "low quality"). A single threshold for all groups can lead to unfair outcomes if the score distributions differ across groups.
*   **The Solution:** STO adjusts the threshold for each subgroup to minimize discrimination, without requiring changes to the underlying machine learning algorithm or the training data.

**3.5 Incorporating Out-of-Preference Data**

Another valuable technique is to incorporate "out-of-preference" data into the policy optimization process. (Arxiv.org) This involves including data that reflects responses to prompts that are *not* part of the standard preference dataset. This can help refine the language model's behavior and make it more robust to variations in input.

**3.6 Causal Inference and Mediation Analysis**

Tools from causal inference and mediation analysis can be used to formalize fairness criteria and constrain the AI's learning process. (Brookings.edu)

*   **Causal Pathways:** These tools help identify the causal pathways through which sensitive features (e.g., race, gender) might influence the AI's actions or outcomes.
*   **Fairness Constraints:** Fairness criteria can be expressed as constraints on these causal pathways, preventing the AI from learning to discriminate based on sensitive features.

**3.7 Report Generation Best Practices**

When generating reports, whether manually or with AI assistance, adhere to these best practices:

*   **Clear Language:** Use plain language that is accessible to a wide audience. (Researchgate.net)
*   **Visualizations:** Use charts and graphs to present data clearly and effectively. (Researchgate.net)
*   **Context:** Provide sufficient context to help readers understand the data and the findings. (Researchgate.net)
*   **Limitations:** Acknowledge the limitations of the analysis and the potential sources of bias. (Researchgate.net)
*   **Conclusions and Recommendations:** Offer clear conclusions and actionable recommendations. (Researchgate.net)
*   **Causation vs. Correlation:** Be careful to distinguish between causation and correlation. (Researchgate.net)
*   **Selection Bias:** Consider potential selection bias in the data. (Researchgate.net)
*   **Confounding Variables:** Identify and address potential confounding variables. (Researchgate.net)
*   **Data Privacy:** Protect the privacy of individuals whose data is used in the analysis. (Researchgate.net)

---

**Part 4: The Future of Equitable AI – Beyond Report Generation**

**4.1 Generalizing GRPO to Other Tasks**

The principles of GRPO can be applied to a wide range of AI tasks beyond technical report generation, including:

*   **Natural Language Processing (NLP):** Machine translation, text summarization, question answering.
*   **Computer Vision:** Image classification, object detection, image generation.
*   **Robotics:** Robot control, navigation, manipulation.
*   **Healthcare:** Medical diagnosis, treatment planning, drug discovery.
*   **Finance:** Credit scoring, fraud detection, algorithmic trading.

**4.2 The Role of Funders and Policymakers**

Funders and policymakers have a crucial role to play in promoting equitable AI development:

*   **Funding Research:** Support research on fairness-aware AI algorithms and techniques, like GRPO.
*   **Promoting Data Sharing:** Encourage the sharing of diverse and representative datasets.
*   **Developing Standards:** Establish clear standards for fairness and accountability in AI systems.
*   **Building Internal Capacity:** Build internal capacity to understand the salience of demographics for various program areas to facilitate equitable policy implementation. (Peakgrantmaking.org)

**4.3 "What If" Scenarios: Exploring the Potential Impact**

*   **What if** all AI systems were trained using GRPO or similar fairness-aware techniques? This could lead to a significant reduction in algorithmic bias and a more equitable distribution of opportunities and resources.
*   **What if** data disaggregation became standard practice in all AI development? This would make it much easier to identify and mitigate bias, leading to fairer outcomes.
*   **What if** we could develop AI systems that were not only fair but also actively promoted social equity? This is a more ambitious goal, but it's one that is worth striving for.

**4.4 The Ethical Imperative**

Building equitable AI is not just a technical challenge; it's an ethical imperative. AI systems have the potential to shape our lives in profound ways. We have a responsibility to ensure that these systems are designed and used in a way that benefits everyone, not just a privileged few.

---

**Conclusion: Towards a Fairer Algorithmic Future**

Group Relative Policy Optimization (GRPO), along with related techniques like Subgroup Threshold Optimization and causal inference methods, offers a powerful toolkit for building more equitable AI systems. By consciously addressing group-level fairness, we can move towards an AI future that is more just and inclusive. This requires a multi-faceted approach, combining technological innovation with a deep understanding of social equity and responsible data practices. The journey towards equitable AI is ongoing, but GRPO represents a significant step in the right direction. The "algorithmic mirror" can reflect a more equitable world, but only if we intentionally design it to do so.

# Sources
- [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblry66IeJLv14vUEmd9hp44Jjwo9PspVig9hJSl6q-f7lbEhSUuAgygrUoGYyCnccxX-YcRpIHgj8U9TXlMb9iMPn15W0mCOxyBJOMLjdnqpjreQa1JxD5oId_zNsHRw5lP7vgRQrgNGEbPUafjS9_gdrZueGGjgkR8tDszr6CaxpdQx_OHksHCrrwxBlnxs4WMT7b820fpa1WwRTVSIPcvQjRxHAVIS76SRDDY-b4eOEwgnwPIbkQS-Uuw==)
- [unite.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrzSmlu_NYBYTudD1Mg2g5jZ7B2QzWX981mwDE71ngREm8fYDzDwMFf4E8F_nqQvEGdV1R2gEanP6VTBS3TwN4u0xw2cD_Zij7bKpsfyjSnJWk1f4YIDnHH6OFM9y0Aj-FfisOkPK9yrVJ8TQV1qDX9OdlnS6PE4cPQBbBGQ7mvrUwQc6f8UedRbtr4dkNExLcRu-045b4YmM37ssF-HZrCGCBViOc-hlf-DFdcgP3iQFO4=)
- [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrycKVqIYuVzJqOWMe-mrum505COV8oSeHCwftETkLitsZfKoVor0wSBk8JMjm9jyIvGjZIOpAAk21atM4jWw9Tx13c2-9cKfYmw-RijgUGw-kbNxMws13eEVuluhFG2kOkpMOqSsgnDrPxffDrG1A2G0-lnEqUt9QmvoWPgaIFPpKp8mgvXTQCa9X-EOaAjkl1mwwSSBzE5eD_I3TtlJUmjWB-k6hMmt9TYlUqPG5Ji4A7H5wTlZTYPdld8i2QokIx-bu0N-w==)
- [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrypzKJ2OsC525KzO8ec_P4jUiq0UoyKqvvb-Sv0wG9uwkNe48r_sEO1lWG9bK2uxg9qiDGo9EJJC7JjkMHkYoVEDbmt0VMGCa0W7S4wZq_9Z098eQZSxhFWmiJi)
- [bridgespan.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrz97PMSRz1D8MiK6a9l7UiaquaK3Nn461ybSI5LTsSUwX3mRlZfY7gjIbm-yUZdB_gB4vIXl1wQ4Zbz00deLuGl1nMJ8kLNcONryetRH5HUOnGePCR17v2Q-wypsGDQnyzrl5lBZrB_CU0yhndwTLSL2y8GHlqnt-osFK9eBBzN8btF3clIY1xzeqMOc9rdWKQ5Ikjdtq56h_NSPrZgt9whoq_3-coMVUD-2SKnX0LFM7_ibQp8yh2WhagTMuvj71WawRrX02afrcbxfWgokNfdBr7GcacUqqDkLA==)
- [soroptimistinternational.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblryLvG4coHAac3UuEA-kyXXSSAcPA3T0J7iIPehtZ0OlmisTwX36a4qnmRfGXuxU4oRtVGWqTPPXkzRx2L56JGkiGHdC5WBbJ1L4EqeQeOEKwLDOUeeULGSxfjA77U7rvYShd2ilojmOv1EGsejzFKhdTMCP8XtIwPXRXLgv0VH4DbC40WFEQCdl7wIc2n0F9972qfyqSNqL30fLgKl31B26jWvs_ZFhSzFo4fF4AFnuSmTG_7L6U6rzYerkXMJRxYx2wSHDLg==)
- [nih.gov](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrwUX6oruXgrO-j6GWyBelUFJu3kapHXSBYx1UODUbzG_8xYN8hxMDLlbABziLK0MtCWjtLDsrQGCaqlYr6mMyg3LOOm-xejXdB3F2UoSaqEtH1qW9MOz_rLGIIzW7YiCZHgORtck84fVx8ynw==)
- [peakgrantmaking.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblryBvgtzFylfgEz4KTJvgHpqY7TbARPV9s2ms6G7HcC4Fk8h1w3Ihvv1Ua-5OJQmolxj6qbytc-AWB3UrE7yuu8OUP5xOaXQZmwah-eZ9V52EnqTWb8nDrYuTagTEB8LRqiTYJBgkV22GqEq_-5JvxwAxxk0HwDoJ-gNYoLXTPUwLpDyguRxoX-qzDfsaKO2OI_G1m8=)
- [mdpi.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrwPOQFYUc1nRe1Rwebhbrjho2yQfD0JyipMqko28et50PT4zGgxRd7-e1DdNCAsMFZS8YPG07NZHk6S3OnkY0m3G9b6g5SZDCLMDGW_tjCp17tpuHT4hp7k9Hjb9iJg2vR8)
- [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrz0SwSuEhIJReUpxTGiY_16nox_9QYUkCOOWw8xJ99eDHrez1klTEaIIWBwxGhtanqauNN5Ja0OMIqOyUFJYLgOFCa0ueAvAasG3ne0jpUC1LDCLGjiGURukwPrpkxOZjZPR43eO53YuY-n2f_cRw==)
- [brookings.edu](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrx3BOxGdMu0hwpLrZCCjYK2Vtj-lOB2RcJkowv-JYGad8xBe3yf9k8BqjyJhN9snjPGHnZBUin32yI7RYNmPF3Iv-bHGHHCFaaZNWc6e0PPI9t3uNJaGb00dclt6H7msvMmGHyYOiU6XswV327bmaR4G4_kSmicm758czK9cvqev7GUTUd930mxwFYiszRZFPsiAQ==)
- [mlr.press](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrz_PHBFJZfRZrMbwnJNWDqpKvaJtz82upB8GSK5VALCEfuOKHVhqMYzTXyZrhDx0mi6A0tZzURCJp-ASpUiFuV-PA13eaITbg_7-tOkQ-m3Xk25EAokjclBVRqg5B5NYyhBM53CsZDRng==)
- [neurips.cc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblryhjGaxt2sNk2_v5edP1vkWby9eWAZr3KzxBYJnNsfCePfuAIHzP201Bxu4u_DmTRijcZ62qFh5bhnAXG0CoEKgAoNURMwcTEnP5RMfAZ36CYeNev5Mvo4lNI8GQdLodPWbagn-QgaWLwKoBJMls4KeYC-tUFI_wmhQVINC24UgM4RpCAbrwCXwehi5IiCdYntFcPI=)
- [facctconference.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrxmLL_ODlj537Ce-rr8NMmqa3UKDpZkgWkkLwq_ImJ9gq99BgeNhGcl_LC8WWqS3d7ChX84f9UKNQgyq9Val2wwa_5W4YVqKJ_Z99maSwIsn6eJHAihiKn32ycs3n5OV6rzAJkhPPLc6rQXSE-8TepXLUb3kUk=)
- [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrxeQPb8UKrHn-cGUxarMBjEawunCpYIzz8CWcSiJTkTkIqvp_zlMiv8u0WoA8SyhS2Cmh1B-hRKhCAmi0v5OLltCxZRdtMC2rgDA0OV458SVrf4iiSq4MblBgQ=)
- [researchgate.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrx7Qb4g8m-Tiy-w33pL2HGD7Db6Iz-ugns5mkIEKhXKqR0C9QXofqe7JeMTOHSDhjV8jS9Gaom8aZuQjWfN7S9kf_lTkUZTkAO2RwN28Ch5FFn9uVNnlOb29IQAONbBAdk9d5_qctFMgfoM9CU1lyDXp1FYaeAE852UmzfAzWYu3jg892ELnIHYyUPQbOt6kbfbFnKLstFb0JMmfxPKYTA40LuCaLPeh_luqM2YeajX7ppsQg==)
- [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrzLCs1Fjl-obwqH13NOHj5Lg9K0BmtNWvNQr5P9LsC8KgLD7j1o6AgutXUVVueJAvKX56fl2lPElpoqkRX-o4vUqo52TFnujiaHO9I9iNaAzXWYx3Ml3tWOm70=)
- [escholarship.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblryy5Vfoy1xAve0U-CNuyqoH5JnuLdLnu5-_fPnZQtrXOl6HXYXQPd9ZiGMUBcVfiKGcn0tcn0AFM_-IwxAtQCdZ7wKLPD3IgFqx7WBU78UuF-MiLFIGDeSw3su85n1_DZRD4bU=)
- [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrxsCfhlUZZkzcf_zrwpXda8T_HL1fVsAgbXDge16Li4njtAW4D2A2jTycTAVBfpoOU0SJB7_t-i-Qk-1AEq-huH5Pf1wFsg9W0jsAX11_3Ff3OUBv8czsfT_eo=)
- [rlhfbook.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrxq_fGBmhamWbt3MKEIvtiRU67g_nlAatFeL2xvUdIIOjduAzqw67FnURKMk1Cs2GXC_Cb2vXehNdmUQ0WLnpDKeX5ztAzqkL7RJjmMKiLPpFXoTgWSHIGxBOv2DXODUexFWAJ7DYXcerQ=)
- [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrzMe1fNpVIZiVkq4FbzsFccghY5EzW_A0BWb4pRiwW1Q1ctAv2PdmvO9dKAZAFl6z-XB-XPYKL_-zgoYdrEOvKDMoa-U9AIvwYrJ7gTGEC_oiWs1mQlQ7FS0hEbA6davZuDd-02XlwEyaLtMsKoTX4KyIU8PSGlCeEuZxU6YwFWKvZl5OmdIMj4Y5itcfB2fWczzxQDv9OB-0bO15zbr9DKF-gWL93YZKo_eS6vQeP7JFUvofU1BL-26xkXLQ==)
- [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrynJz9VsU7-W_4AT4bYjbaH5IpgEv0lHqdT0d229QtSpmEbj9VEpvn18kTEE_Wt20fT2B5tJGAQGfoe0wq4Vkgg5JyUeaHauPfvNeGw-v72vQgY3F5sB_JJPig=)
- [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AQXblrxWBerEcPBHU8LU7BKHwdcsGcXZlMAxucLGEzogiEm1yvNRwJ7-Qxrq1UcbeZACZdnmdInGkpTBa13xhwLScjcW1sGQbNsoQy-nvb8qrdpMWaRmUoFl870F9q8=)

Total research time: 5 minutes and 48 seconds