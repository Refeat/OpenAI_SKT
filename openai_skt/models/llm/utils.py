from pathlib import Path

from langchain.prompts.prompt import PromptTemplate
from langchain.prompts.loading import _load_output_parser
import langchain.prompts.loading as loading_module

def _load_template(var_name: str, config: dict) -> dict:
    """Load template from the path if applicable."""
    # Check if template_path exists in config.
    if f"{var_name}_path" in config:
        # If it does, make sure template variable doesn't also exist.
        if var_name in config:
            raise ValueError(
                f"Both `{var_name}_path` and `{var_name}` cannot be provided."
            )
        # Pop the template path from the config.
        template_path = Path(config.pop(f"{var_name}_path"))
        # Load the template.
        if template_path.suffix == ".txt":
            with open(template_path, encoding='utf-8') as f:
                template = f.read()
        else:
            raise ValueError
        # Set the template variable to the extracted variable.
        config[var_name] = template
    return config

def _load_prompt(config: dict) -> PromptTemplate:
    """Load the prompt template from config."""
    # Load the template from disk if necessary.
    config = _load_template("template", config)
    config = _load_output_parser(config)
    return PromptTemplate(**config)

loading_module.type_to_loader_dict["prompt"] = _load_prompt