"""
requires crfm-helm v0.2.3 
currently only available via pip install crfm-helm@git+https://github.com/stanford-crfm/helm.git@main
"""
from typing import (
    Any,
    Dict,
    List,
    Mapping,
    Optional,
    Union,
    Tuple,
)

import os

from helm.common.authentication import Authentication
from helm.common.request import Request, RequestResult
from helm.proxy.services.remote_service import RemoteService

import asyncio
from functools import partial

from langchain.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,

)
from langchain.schema import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    ChatGeneration,
    ChatResult,
    HumanMessage,
    SystemMessage,
)

from langchain.chat_models.base import SimpleChatModel


def _convert_message_to_dict(message: BaseMessage) -> dict:
    if isinstance(message, ChatMessage):
        message_dict = {"role": message.role, "content": message.content}
    elif isinstance(message, HumanMessage):
        message_dict = {"role": "user", "content": message.content}
    elif isinstance(message, AIMessage):
        message_dict = {"role": "assistant", "content": message.content}
    elif isinstance(message, SystemMessage):
        message_dict = {"role": "system", "content": message.content}
    else:
        raise ValueError(f"Got unknown type {message}")
    if "name" in message.additional_kwargs:
        message_dict["name"] = message.additional_kwargs["name"]
    return message_dict


class crfmChatLLM(SimpleChatModel):
    
    """Wrapper around crfm chat language models.

    To use, you should have the ``crfm-helm`` python package installed, and the
    environment variable ``CRFM_API_KEY`` set with your API key.

    Any parameters that are valid to be passed to the openai.create call can be passed
    in, even if not explicitly saved on this class.

    Example:
        .. code-block:: python

            from crfm_chat_llm import crfmChatLLM
            chat = crfmChatLLM(model_name="openai/gpt-4-0314")

            system_message = SystemMessage(content="You are a helpful AI Assistant.")
            human_message_0 = HumanMessage(content="Tell me a joke")
            assistant_message_0 = AIMessage(content="What do you call a cat that can do magic tricks? A magic kit.")
            human_message_1 = HumanMessage(content="This joke was not funny, tell me one about dogs.") 

            messages = [
                system_message,
                human_message_0,
                assistant_message_0,
                human_message_1,
            ]

            response = chat.generate([messages], stop=["System:"])
    """

    client: Any  #: :meta private:
    model_name: str = "openai/gpt-4-0314"
    """Model name to use."""
    temperature: float = 0.7
    """What sampling temperature to use."""
    max_tokens: int = 200 
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
    """api key."""
    max_retries: int = 5
    """Maximum number of retries to make when generating."""
    echo_prompt: bool = False
    """Whether to echo the prompt in the response."""
    verbose: bool = True 
    """Whether to print out the prompt and response"""
    messages: Optional[List[BaseMessage]]
    """Used for chat models. (OpenAI only for now).
    if messages is specified for a chat model, the prompt is ignored.
    Otherwise, the client should convert the prompt into a message."""
    request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    """Timeout for requests to OpenAI completion API. Default is 600 seconds."""
    streaming: bool = False
    """Whether to stream the results or not."""
        
    @property
    def _llm_type(self) -> str:
        return "CRFM"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> ChatResult:
        message_dicts = [_convert_message_to_dict(m) for m in messages]
        output_str = self._call(message_dicts, stop=stop, run_manager=run_manager)
        message = AIMessage(content=output_str)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])


    def _call(self, 
              messages: List[BaseMessage],
              stop: Optional[List[str]] = [],
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              ) -> str:
        
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
                    print(messages)
                request = Request(model=self.model_name,
                                  messages=messages,
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
        return {**{"model_name": self.model_name}, **self._default_params}
    
    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling OpenAI API."""
        return {
            "model": self.model_name,
            "request_timeout": self.request_timeout,
            "max_tokens": self.max_tokens,
            "stream": self.streaming,
            "n": self.num_completions,
            "temperature": self.temperature,
        }
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    ) -> ChatResult:
        func = partial(self._generate, messages, stop=stop, run_manager=run_manager)
        return await asyncio.get_event_loop().run_in_executor(None, func)