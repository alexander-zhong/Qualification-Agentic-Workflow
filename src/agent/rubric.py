from typing_extensions import TypedDict
from typing import Annotated, Optional, Literal





# !important the key must match the same one in the state.


COMPANY_RUBRIC = {
    "company_mission_alignment": """
    Title: Company Mission Alignment
    Description: This factor assesses the alignment between the company's mission and the event's goals. Companies focused on education, student development, or similar values are more likely to recognize mutual benefits in sponsoring the event.
    Score Table:
    5. Perfect alignment. The company's mission and vision are directly aligned with the core goals of the event. They have a strong commitment to the same values or objectives as the club's event, and their company has a focus on education for students. Companies focused on education, student development, or similar values are more likely to recognize mutual benefits in sponsoring the event.
    4. Strong alignment. The company's mission is closely related to the event's theme, with clear goals that support the objectives of the event. Their mission actively promotes elements like development, innovation, or relevant skills, making them a good fit for the event.
    3. Moderate alignment. The company's mission includes aspects that relate to the club's event theme, but these are not the primary focus of their vision. There is some overlap, but it's not central to the company's overall goals.
    2. Minimal alignment. The company may have some relevance to the event's theme, but it is not a central part of their mission. Their goals might indirectly benefit from the event, but their core mission does not align closely with the subject of the event.
    1. No alignment. The company's mission and vision are entirely unrelated to the theme or goals of club event. Their focus is in a different industry or area, and their mission does not contribute to or support the objectives of our event in any meaningful way.
    """,
    
    "relevant_events": """
    Title: Relevant Events
    Description: This measures the company's recent involvement or activity in areas related to the event's theme. Looking for companies that have recently participated in or organized similar events demonstrates ongoing commitment and increases the chance of mutual benefits.
    Score Table:
    5. Company is deeply involved in the subject of our event. They are actively acquiring companies, forming partnerships, or publishing high-quality content (like blogs, research papers, or videos) directly tied to our event's theme. This demonstrates ongoing commitment to the subject meaning there is a higher chance of companies seeing mutual benefits for sponsoring our event.
    4. The company has actively engaged in our event's subject matter through several initiatives. This could be through strategic partnerships, relevant acquisitions, or regularly publishing blog posts that show a strong interest in the topic of our event.
    3. The company has shown moderate involvement in topics related to our event. They may have done a partnership or acquisition, or written a few relevant blog posts recently, but their connection to the event's subject isn't core to their business.
    2. The company has minimal or outdated activity related to the event's theme. Perhaps they've published one or two blog posts in the past, but there's no clear ongoing focus or initiative connected to our event's subject.
    1. The company has no recent activity related to the event's theme. They haven't made any acquisitions, formed partnerships, or published content that aligns with the subject of club event.
    """,
    
    "sponsorship_history": """
    Title: Past Sponsorship History
    Description: This assesses the company's track record of sponsoring hackathons, student events, or university initiatives. It looks at both frequency and depth of involvement. Greater previous sponsor frequency means there is a higher chance of partnership with our club.
    Score Table:
    5. Extensive and frequent sponsorship history. Known for being a major supporter of hackathons and student events, sponsoring numerous events each year and actively seeking out these opportunities. Greater previous sponsor frequency means there is a higher chance of partnership with our club.
    4. Consistent sponsorship history. Regularly sponsors hackathons and student events, typically multiple times per year across various clubs or organizations.
    3. Moderate sponsorship history. Occasionally sponsors hackathons or student events, averaging about once a year or every other year.
    2. Minimal sponsorship history. Has sponsored one or two hackathons or student events in the past, but very infrequently (example: once every few years).
    1. No history of sponsoring hackathons or student events. Company has never engaged in this type of sponsorship before.
    """,
    
    "geographic_relevance": """
    Title: Geographic Relevance
    Description: This assesses the company's operational presence in our region, especially in or near Vancouver or British Columbia. Companies with a local presence are more likely to engage and support events within their communities and have the ease of sending a representative to attend events in person.
    Score Table:
    5. Directly based in or around Vancouver. Company is headquartered in Vancouver or has major operations in the Greater Vancouver Area or nearby cities (e.g., Seattle, Victoria), demonstrating a strong local commitment and presence.
    4. Strong presence in the Pacific Northwest region. Company has significant operations or customer base in the Pacific Northwest (e.g., British Columbia, Washington, Oregon), showing clear interest in this specific region.
    3. Some regional presence. Company has a presence in the Pacific Northwest (e.g., British Columbia, Washington, Oregon). This indicates some level of connection and interest in our region.
    2. Presence in North America, but limited to the United States or other regions of North America.
    1. No presence in North America. Company operates exclusively in other continents with no apparent interest or connections to the North American market.
    """
}




SPEAKER_RUBRIC = {
    "speaker_expertise_alignment": """
    Title: Speaker Expertise Alignment
    Description: This evaluates how closely the speaker's expertise aligns with the goals of the event. Speakers with backgrounds more closely related to event theme can bring more value, especially speakers that had a past focus in university events.
    Score Table:
    5. Perfect alignment. The speaker's expertise and experiences directly match the core goals of the event. They have a proven track record of contributing to similar events or discussions and bring significant depth to the topic. Speakers with backgrounds that is more closely related to event theme can bring more value, especially speakers that had a past focus in university events.
    4. Strong alignment. The speaker's expertise is closely related to the event theme, with clear knowledge and experience that support the event's goals. Their background actively promotes relevant skills or knowledge areas.
    3. Moderate alignment. The speaker's background includes aspects that relate to the event's theme, but these are not their main focus. There is some overlap, but it's not central to their work.
    2. Minimal alignment. The speaker may have some experience related to the event's theme, but it's not a central part of their expertise. Their involvement would bring limited benefits.
    1. No alignment. The speaker's expertise is entirely unrelated to the event theme. Their background does not contribute to or support the event's objectives in any meaningful way.
    """,
    
    "company_relevance": """
    Title: Company or Organization Relevance
    Description: This criterion evaluates how closely the speaker's company or organization aligns with the event's theme. Speakers from organizations directly involved in the event theme are more likely to see mutual benefits.
    Score Table:
    5. Perfect alignment. The speaker's company is a leader in the field directly connected to the event's theme. The organization is known for pioneering work, products, or services in this area, making them an ideal fit for our event.
    4. Strong relevance. The speaker's company is actively engaged in the event's theme, with regular involvement or business operations that directly relate to it. The organization's goals and activities closely match the objectives of our event.
    3. Moderately relevant. The speaker's company has a clear connection to the event theme. It may not be their core business, but they have ongoing projects, products, or initiatives that align with the subject of the event.
    2. Limited relevance. The speaker's company has some connection to the event theme, but it is not a primary focus. The organization might have occasional projects or initiatives related to the theme, but they are not central to its operations.
    1. Unrelated organization. The speaker's company operates in a field completely unrelated to the event's theme. Their organization does not contribute to or support the objectives of our event in any meaningful way.
    """,
    
    "geographic_relevance": """
    Title: Geographic Relevance
    Description: This assesses the speaker's presence in our region, especially in or near Vancouver or British Columbia. Speakers with a local presence are more likely to engage and support events within their communities and be able to attend events in person.
    Score Table:
    5. Local to Vancouver. The speaker is based directly in Vancouver or the Greater Vancouver Area, or their company is headquartered or has major operations there. This shows a strong local commitment, making them an ideal candidate for our event.
    4. Strong regional presence. The speaker's company has significant operations or a customer base in the Pacific Northwest, including British Columbia, showing ongoing engagement and relevance to our area.
    3. Some regional presence. The speaker or their company has a presence in the Pacific Northwest (e.g., British Columbia, Washington, Oregon). This indicates some level of connection and interest in our region, even if not the primary focus.
    2. Presence in North America, but not locally. The speaker is based in the United States or another part of North America, but their company does not have strong ties to the Pacific Northwest or British Columbia.
    1. No local presence. The speaker is based outside of North America, and their company operates exclusively on other continents, with no apparent interest or connections to the North American market.
    """
}