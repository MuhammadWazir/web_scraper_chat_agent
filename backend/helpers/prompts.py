from configs.constants import PROMPTS


def compile_assets(website_text: str, audience_context: str) -> dict:
	return {
		key: template.format(website_text=website_text, audience_context=audience_context)
		for key, template in PROMPTS.items()
	} 