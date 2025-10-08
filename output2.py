<think>
Okay, so I need to figure out how to refactor the given code to address the issue where the model is returning a 413 error because the request is too large. The error message mentions that the request exceeds the token limit, so the main problem is that the code snippets being sent are too long.

First, I should look at where the code snippets are being processed. The _generate_single_summary method is where the prompt is created. The current code takes the entire code_snippet and puts it into the prompt. If the code_snippet is very long, this will make the prompt too large, exceeding the model's token limit.

So, the solution is to truncate the code snippet to a manageable size before sending it to the model. I need to decide on a maximum length. Maybe something like 600 characters, which should be under the token limit for most models.

I'll add a new method called _truncate_code_snippet that takes the code and a max_length. It checks if the code is longer than max_length and truncates it, adding an ellipsis at the end to indicate it's been shortened.

Next, I'll modify the _create_summary_prompt method to use this truncated code. Instead of using the full code_snippet, it'll use the truncated version. Also, I'll add a log message in _generate_single_summary to note when a code snippet is truncated.

I should also ensure that the rest of the code remains functional. The public API shouldn't change, so the method signatures and interactions with other parts of the system stay the same.

I'll go through the code step by step. In the _generate_single_summary method, after extracting the code_snippet, I'll call the new truncate method. Then, when creating the prompt, I'll use the truncated code. I'll also add a debug log to indicate truncation.

I need to make sure that all other parts of the code, like error handling and memory cleanup, remain intact. The refactored code should only address the token limit issue without introducing new bugs.

Finally, I'll test the changes to ensure that the code snippets are being truncated correctly and that the model no longer returns the 413 error. This should fix the problem without affecting the overall functionality of the AnnotatorAgent.
</think>

async def _generate_single_summary(self, entity) -> tuple:
    """Generate summary for a single entity with proper error handling."""
    try:
        # Extract code and entity name
        code_snippet = getattr(entity, 'code', '')
        entity_name = getattr(entity, 'type', '')
        entity_id = getattr(entity, 'unique_id', 'unknown')

        if code_snippet == '':
            logger.warning(f"Entity {entity_id} has no code details")
            return entity, "No code details available.", None

        # Truncate code snippet to prevent token limit exceeded errors
        max_code_length = 600  # Adjust based on model token limits
        code_snippet = self._truncate_code_snippet(code_snippet, max_code_length)

        logger.debug(f"Processing entity {entity_id} ({entity_name})")
        logger.debug(f"Code snippet length: {len(code_snippet)} chars")
        logger.debug(f"Code preview: {code_snippet[:100]}...")

        prompt = self._create_summary_prompt(code_snippet, entity_name)

        logger.debug(f"Generating summary for entity {entity_id}")

        raw_summary = self.model.generate(prompt)

        summary = self._clean_summary(raw_summary)
        logger.debug(f"Generated summary for {entity_id}: {summary[:50]}...")

        return entity, summary, None

    except Exception as e:
        logger.error(f"Error generating summary for entity {getattr(entity, 'unique_id', 'unknown')}: {str(e)}")
        return entity, "Function summary unavailable due to generation error.", str(e)

def _truncate_code_snippet(self, code: str, max_length: int = 600) -> str:
    """Truncate code snippet to prevent token limit exceeded errors."""
    if len(code) <= max_length:
        return code
    return code[:max_length] + "..."