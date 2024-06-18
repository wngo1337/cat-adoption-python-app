from enum import Enum
import os
import google.generativeai as genai


class DescriptionGenerator:
    """A static class that provides data types and methods to generate prompts and responses about cats based on their traits"""

    CAT_SUMMARY_PROMPT_TEMPLATE = """Write a one paragraph summary about a cat
    named {0} that reflects the cat's {1} personality and {2} appearance.
    Include a line about the cat's purpose and desires, but do not include the
    specific trait words unless it enhances the summary."""
    # Two parameters required
    CAT_DESCRIPTION_PROMPT_TEMPLATE = """Write a short, second-person
    description about a cat named {0} looking at the reader inside the adoption
    agency. The description must reflect the cat's {1} personality and {2}
    appearance, though it does not need to include the specific trait words.
    The text should be no longer than a paragraph."""
    CAT_ADOPT_PROMPT_TEMPLATE = """Write a short, second-person description
    about the user {0} adopting a cat named {1} from the adoption agency. Both
    adopter and cat are very happy. The description must reflect the cat's {2}
    personality and {3} appearance, though it does not need to include the
    specific trait words. The text should be no longer than a paragraph."""
    # Two parameters required
    CAT_PLAY_PROMPT_TEMPLATE = """Write a short description about a cat named
    {0} playing outside an adoption agency with their owner {1}. The
    description must reflect the cat's {2} personality and {3} appearance,
    though it does not need to include the specific trait words. The text
    should be no longer than a paragraph."""
    # Three parameters required
    CONTEMPLATE_STEAL_PROMPT_TEMPLATE = """Write a short, second-person
    description about a thief named {0} who is thinking about stealing a cat
    named {1} from their owner {2} as they notice a moment of opportunity. The
    description must reflect the cat's {3} personality and {4} appearance,
    though it does not need to include the specific trait words. The text
    should be no longer than a paragraph."""
    # Three parameters required
    CAT_STEAL_PROMPT_TEMPLATE = """Write a short, second-person description
    about a thief named {0} stealing a cat named {1} from their owner {2} while
    their back is turned. The description must reflect the cat's {3}
    personality and {4} appearance, though it does not need to include the
    specific trait words. Only write about the act of the theft itself instead
    of the leadup to it. You must include a line about the owner chasing the
    thief down the street but being too slow as they escape. Ask the thief if
    they are happy with their actions. The text should be no longer than a
    paragraph."""
    # Three parameters required
    CAT_WISDOM_PROMPT_TEMPLATE = """You are a cat named {0} with a {1}
    personality and {2} appearance having a friendly conversation with your
    owner. When given input, you should reply with a third-person description
    of yourself guiding the user to the answer through gestures, actions, and
    speech. Your replies may be up to three paragraphs long, and they should
    reflect the nature of your personality and appearance, but they should
    always be friendly. Follow direct quotations with the term NEWPARAGRAPH
    unless it is the very last line."""

    class DescriptionType(Enum):
        """An Enum class defining different types of possible scenario descriptions for cats."""

        CAT_SUMMARY = 1
        CAT_DESCRIPTION = 2
        CAT_ADOPT = 3
        CAT_PLAY = 4
        CONTEMPLATE_STEAL = 5
        CAT_STEAL = 6
        CAT_WISDOM = 7

    description_types_to_prompt_templates = {
        DescriptionType.CAT_SUMMARY: CAT_SUMMARY_PROMPT_TEMPLATE,
        DescriptionType.CAT_DESCRIPTION: CAT_DESCRIPTION_PROMPT_TEMPLATE,
        DescriptionType.CAT_ADOPT: CAT_ADOPT_PROMPT_TEMPLATE,
        DescriptionType.CAT_PLAY: CAT_PLAY_PROMPT_TEMPLATE,
        DescriptionType.CONTEMPLATE_STEAL: CONTEMPLATE_STEAL_PROMPT_TEMPLATE,
        DescriptionType.CAT_STEAL: CAT_STEAL_PROMPT_TEMPLATE,
        DescriptionType.CAT_WISDOM: CAT_WISDOM_PROMPT_TEMPLATE,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
    model = genai.GenerativeModel("gemini-1.5-flash")
    genai.configure(api_key=GOOGLE_API_KEY)

    @staticmethod
    def create_formatted_prompt(description_type, values):
        """Generates a prompt based on the DescriptionType value passed in, using the provided values to do so."""
        return DescriptionGenerator.description_types_to_prompt_templates[
            description_type
        ].format(*values)

    @staticmethod
    def generate_response(prompt):
        """Generates a response via the Gemini API, based on the prompt passed in."""
        response = DescriptionGenerator.model.generate_content(
            prompt, safety_settings=DescriptionGenerator.safety_settings
        )
        return response.text

    @staticmethod
    def generate_response_from_history(context, user_input):
        """Generates a response for an existing conversation, using
        conversation history as context for the reply, and returns a tuple
        containing the response and the updated chat context."""
        context.append({"role": "user", "parts": [user_input]})
        response = DescriptionGenerator.model.generate_content(context)
        # Add the model's top reply to the ongoing chat history before we
        # pass it back
        reply_parts = []
        for part in response.candidates[0].content.parts:
            reply_parts.append(part.text)
        context.append({"role": "model", "parts": reply_parts})

        return (response.text, context)
