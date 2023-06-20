import os
import logging
import sys
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Union,
)

from pydantic import BaseModel, Extra, Field, root_validator

from langchain.llms.base import BaseLLM
from langchain.schema import Generation, LLMResult
from langchain.utils import get_from_dict_or_env

from helm.common.authentication import Authentication
from helm.common.perspective_api_request import PerspectiveAPIRequest, PerspectiveAPIRequestResult
from helm.common.request import Request, RequestResult
from helm.common.tokenization_request import TokenizationRequest, TokenizationRequestResult
from helm.proxy.accounts import Account
from helm.proxy.services.remote_service import RemoteService
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any


class crfmLLM(LLM):
    
    """Wrapper around crfm large language models.

    To use, you should have the ``crfm-helm`` python package installed, and the
    environment variable ``CRFM_API_KEY`` set with your API key.

    Any parameters that are valid to be passed to the openai.create call can be passed
    in, even if not explicitly saved on this class.

    Example:
        .. code-block:: python

            from crfm_llm import crfmLLM
            openai = crfmLLM(model_name="openai/text-davinci-003")
    """

    client: Any  #: :meta private:
    model_name: str = "openai/text-davinci-003"
    """Model name to use."""
    temperature: float = 0.7
    """What sampling temperature to use."""
    max_tokens: int = 300 
    """The maximum number of tokens to generate in the completion.
    -1 returns as many tokens as possible given the prompt and
    the models maximal context size."""
    top_p: float = 1
    """Total probability mass of tokens to consider at each step."""
    frequency_penalty: float = 0
    """Penalizes repeated tokens according to frequency."""
    presence_penalty: float = 0
    """Penalizes repeated tokens."""
    num_completions: int = 1
    """How many completions to generate for each prompt."""
    top_k_per_token: int = 1
    """number of candidates per token position in each completion"""
    crfm_api_key: Optional[str] = None 
    max_retries: int = 5
    """Maximum number of retries to make when generating."""
    echo_prompt: bool = False
    """Whether to echo the prompt in the response."""
    verbose: bool = True 
    """Whether to print out the prompt and response"""
        
    @property
    def _llm_type(self) -> str:
        return "CRFM"
    
    def _call(self, prompt: str, 
              stop: Optional[List[str]] = []) -> str:
        # get api key from environment
        if self.crfm_api_key is None:
            self.crfm_api_key = os.getenv("CRFM_API_KEY")
        auth = Authentication(api_key=self.crfm_api_key)
        service = RemoteService("https://crfm-models.stanford.edu")


        # Make a request
        tries = 0
        result = None
        while tries < self.max_retries:
            try:
                tries += 1
                if self.verbose:
                    print(prompt)
                request = Request(model=self.model_name,
                                prompt=prompt,
                                temperature=self.temperature,
                                max_tokens=self.max_tokens,
                                top_p=self.top_p,
                                frequency_penalty=self.frequency_penalty,
                                presence_penalty=self.presence_penalty,
                                num_completions=self.num_completions,
                                top_k_per_token=self.top_k_per_token,
                                stop_sequences=stop,
                )

                request_result: RequestResult = service.make_request(auth, request)
                result = request_result.completions[0].text
                if self.verbose:
                    print('------------------')
                    print(result)
            except Exception as e:
                print(f"Error: {e}, retrying... ({tries}/{self.max_retries})")
                continue
            break

        assert result is not None
        return result
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"num_completions": self.num_completions,
                "model_name": self.model_name,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": self.top_p,
                "frequency_penalty": self.frequency_penalty,
                "presence_penalty": self.presence_penalty,
                "top_k_per_token": self.top_k_per_token,
                "crfm_api_key": self.crfm_api_key,
                "request_timeout": self.request_timeout,
                "max_retries": self.max_retries,
                "echo_prompt": self.echo_prompt,
                }
    
    def echo_prompt(self, prompt: str) -> LLMResult:
        # get api key from environment
        if self.crfm_api_key is None:
            self.crfm_api_key = os.getenv("CRFM_API_KEY")
        auth = Authentication(api_key=self.crfm_api_key)
        service = RemoteService("https://crfm-models.stanford.edu")
        request = Request(model=self.model_name,
            prompt=prompt,
            echo_prompt=True,
            temperature=self.temperature,
            max_tokens=0,
            top_p=self.top_p,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            num_completions=self.num_completions,
            top_k_per_token=self.top_k_per_token,
        )
        request_result: RequestResult = service.make_request(auth, request)
        result = request_result.completions[0]
        return result