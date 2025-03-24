"""
This script demonstrates how to run the OWL system with an open-source model
on VLLM as the user agent.

Pre-requisites: bash scripts/serve.sh (4 GPUs for qwen2.5-vl-7b-instruct).
"""

from dotenv import load_dotenv
load_dotenv()

import os
from loguru import logger

from camel.models import ModelFactory
from camel.toolkits import (
    AudioAnalysisToolkit,
    CodeExecutionToolkit,
    DocumentProcessingToolkit,
    ExcelToolkit,
    ImageAnalysisToolkit,
    SearchToolkit,
    VideoAnalysisToolkit,
    WebToolkit,
)
from camel.types import ModelPlatformType, ModelType
from camel.configs import ChatGPTConfig

from utils import GAIABenchmark


# Configuration
LEVEL = 1
SAVE_RESULT = True
test_idx = [0]
VLLM_MODEL_TYPE = "Qwen/Qwen2.5-VL-7B-Instruct"  # set the VLLM model type
PORT = 8964  # set the port for the VLLM model
SAVE_TO = "results/result_vllm.json"


def main():
    """Main function to run the GAIA benchmark."""
    # Create cache directory
    cache_dir = "tmp/"
    os.makedirs(cache_dir, exist_ok=True)

    # Create models for different components
    models = {
        "user": ModelFactory.create(
            model_platform=ModelPlatformType.VLLM,
            model_type=VLLM_MODEL_TYPE,
            model_config_dict={"temperature": 0., "top_p": 1.},
            url=f"http://localhost:{PORT}/v1",
        ),
        "assistant": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict=ChatGPTConfig(temperature=0, top_p=1).as_dict(),
        ),
        "web": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict=ChatGPTConfig(temperature=0, top_p=1).as_dict(),
        ),
        "planning": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict=ChatGPTConfig(temperature=0, top_p=1).as_dict(),
        ),
        "video": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict=ChatGPTConfig(temperature=0, top_p=1).as_dict(),
        ),
        "image": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict=ChatGPTConfig(temperature=0, top_p=1).as_dict(),
        ),
        "search": ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=ModelType.GPT_4O,
            model_config_dict=ChatGPTConfig(temperature=0, top_p=1).as_dict(),
        ),
    }
    
    # Configure toolkits
    tools = [
        *WebToolkit(
            headless=True,  # Set to True for headless mode (e.g., on remote servers)
            web_agent_model=models["web"],
            planning_agent_model=models["planning"],
        ).get_tools(),
        *DocumentProcessingToolkit().get_tools(),
        *VideoAnalysisToolkit(model=models["video"]).get_tools(),  # This requires OpenAI Key
        *AudioAnalysisToolkit().get_tools(),  # This requires OpenAI Key
        *CodeExecutionToolkit(sandbox="subprocess", verbose=True).get_tools(),
        *ImageAnalysisToolkit(model=models["image"]).get_tools(),
        *SearchToolkit(model=models["search"]).get_tools(),
        *ExcelToolkit().get_tools(),
    ]
    
    # Configure agent roles and parameters
    user_agent_kwargs = {"model": models["user"]}
    assistant_agent_kwargs = {"model": models["assistant"], "tools": tools}

    # Initialize benchmark
    benchmark = GAIABenchmark(
        data_dir="data/gaia",
        save_to=SAVE_TO,
    )

    # Print benchmark information
    print(f"Number of validation examples: {len(benchmark.valid)}")
    print(f"Number of test examples: {len(benchmark.test)}")

    # Run benchmark
    result = benchmark.run(
        on="valid", 
        level=LEVEL, 
        idx=test_idx,
        save_result=SAVE_RESULT,
        user_role_name="user",
        user_agent_kwargs=user_agent_kwargs,
        assistant_role_name="assistant",
        assistant_agent_kwargs=assistant_agent_kwargs,
    )

    # Output results
    logger.success(f"Correct: {result['correct']}, Total: {result['total']}")
    logger.success(f"Accuracy: {result['accuracy']}")


if __name__ == "__main__":
    main()
