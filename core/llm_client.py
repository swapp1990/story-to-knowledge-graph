import os
import re
import json
import logging
import threading
from datetime import datetime
import base64
from typing import Dict, Any, Generator, List, Optional
from openai import OpenAI
from flask import jsonify
from core.utils import clean_json_string

class LLMClient:
	def __init__(self):
		self.selected_llm_main = os.getenv('SELECTED_LLM_MAIN', 'OPENAI').upper()
		self.selected_llm_nsfw = os.getenv('SELECTED_LLM_NSFW', 'GROK').upper()
		print("selected_llm_main:", self.selected_llm_main)
		print("selected_llm_nsfw:", self.selected_llm_nsfw)
		
		# Get configuration based on selected LLM
		self.main_api_key = os.getenv(f'{self.selected_llm_main}_API_KEY')
		self.main_api_base = os.getenv(f'{self.selected_llm_main}_API_BASE')
		self.main_model = os.getenv(f'{self.selected_llm_main}_MODEL')

		self.nsfw_api_key = os.getenv(f'{self.selected_llm_nsfw}_API_KEY')
		self.nsfw_api_base = os.getenv(f'{self.selected_llm_nsfw}_API_BASE')
		self.nsfw_model = os.getenv(f'{self.selected_llm_nsfw}_MODEL')
		
		if not all([self.main_api_key, self.main_api_base, self.main_model]):
			raise ValueError(f"Missing configuration for {self.selected_llm_main}")

		if not all([self.nsfw_api_key, self.nsfw_api_base, self.nsfw_model]):
			raise ValueError(f"Missing configuration for {self.selected_llm_nsfw}")

		# Initialize main client
		self.main_client = OpenAI(
			api_key=self.main_api_key,
			base_url=self.main_api_base,
		)

		# Initialize nsfw client
		self.nsfw_client = OpenAI(
			api_key=self.nsfw_api_key,
			base_url=self.nsfw_api_base,
		)
		self.logger = logging.getLogger(__name__)
		self.cancel_event = threading.Event()
		
		# Set up error logging to file
		self.setup_error_logging()

	def setup_error_logging(self):
		"""Setup logging to write errors to a file in the data folder"""
		log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs')
		os.makedirs(log_dir, exist_ok=True)
		
		error_log_file = os.path.join(log_dir, 'llm_errors.log')
		file_handler = logging.FileHandler(error_log_file)
		file_handler.setLevel(logging.ERROR)
		
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		file_handler.setFormatter(formatter)
		
		self.logger.addHandler(file_handler)

	def _get_client_and_model(self, model: str = None, nsfw: bool = False):
		"""
		Returns the appropriate client and model based on the parameters.
		Since we're using a single LLM configuration, we always return the main client
		"""
		if nsfw:
			return self.nsfw_client, self.nsfw_model
		return self.main_client, model or self.main_model

	def reset_cancel_event(self):
		self.cancel_event.clear()

	def cancel_generation(self):
		print("CANCEL_GENERATION")
		self.cancel_event.set()

	def get_available_models(self) -> List[str]:
		"""
		Get the list of available models.
		"""
		return self.available_models

	def get_current_model(self) -> str:
		"""
		Get the currently selected model.
		"""
		return self.current_model

	def set_current_model(self, model: str) -> None:
		"""
		Set the current model.
		"""
		if model not in self.available_models:
			raise ValueError(f"Invalid model: {model}. Available models are: {', '.join(self.available_models)}")
		self.current_model = model

	def _get_client_and_model(self, model: str = None, nsfw: bool = False):
		if nsfw:
			return self.nsfw_client, self.nsfw_model
		return self.main_client, model or self.main_model

	def generate_json(
		self,
		prompt: str,
		system_prompt: str,
		model: str = None,
		temperature: float = 0.7,
		max_tokens: int = 10000,
		nsfw: bool = False,
	) -> Dict[str, Any]:
		client, model = self._get_client_and_model(model, nsfw)
		print("generate_json:", model)
		try:
			response = client.chat.completions.create(
				model=model,
				messages=[
					{"role": "system", "content": system_prompt},
					{"role": "user", "content": prompt}
				],
				temperature=temperature,
				max_tokens=max_tokens
			)
			
			content = response.choices[0].message.content
			content = clean_json_string(content)
			
			return content

		except json.JSONDecodeError as e:
			self.logger.error(f"Failed to parse response as JSON: {e}")
			return jsonify({'error': "Failed to generate valid JSON response"}), 500

		except Exception as e:
			self.logger.error(f"Error in generate_json: {str(e)}")
			return jsonify({'error': "An error occurred while processing the request"}), 500

	def _validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> None:
		"""
		Validate the generated JSON against the provided schema.
		This is a simple implementation and can be extended with a full JSON schema validator like jsonschema.
		"""
		def validate_object(obj, obj_schema):
			for key, value_schema in obj_schema.get("properties", {}).items():
				if key not in obj:
					if key in obj_schema.get("required", []):
						raise ValueError(f"Missing required key: {key}")
					continue
				if value_schema.get("type") == "object":
					validate_object(obj[key], value_schema)
				elif value_schema.get("type") == "array":
					for item in obj[key]:
						validate_object(item, value_schema["items"])

		validate_object(data, schema)

	# You can add other methods from the original app.py here, such as:
	def generate_text(self, prompt: str, system_prompt: str, model: str = None, temperature: float = 0.7, max_tokens: int = 1000, nsfw: bool = False):
		client, model = self._get_client_and_model(model, nsfw)
		print("generate_text:", model)
		response = client.chat.completions.create(
			model=model,
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": prompt}
			],
			temperature=temperature,
			max_tokens=max_tokens
		)
		return response.choices[0].message.content

	def generate_streamed_json(
		self,
		prompt: str,
		system_prompt: str,
		model: str = None,
		temperature: float = 0.7,
		max_tokens: int = 1000,
		nsfw: bool = False,
	) -> Generator[Dict[str, Any], None, None]:
		client, model = self._get_client_and_model(model, nsfw)
		print("generate_streamed_json:", model)
		try:
			response = client.chat.completions.create(
				model=model,
				messages=[
					{"role": "system", "content": system_prompt},
					{"role": "user", "content": prompt}
				],
				temperature=temperature,
				max_tokens=max_tokens,
				stream=True,
				stream_options={"include_usage": True}
			)
			yield from self._process_json_stream(response)
		except Exception as e:
			self.logger.error(f"Error in generate_streamed_json: {str(e)}")
			yield {"error": f"An error occurred: {str(e)}"}
	
	def generate_streamed_text(
		self,
		prompt: str,
		system_prompt: str,
		model: str = None,
		temperature: float = 0.7,
		max_tokens: int = 10000,
		nsfw: bool = False
	) -> Generator[Dict[str, Any], None, None]:
		client, model = self._get_client_and_model(model, nsfw)
		print("generate_streamed_text:", model)
		try:
			response = client.chat.completions.create(
				model=model,
				messages=[
					{"role": "system", "content": system_prompt},
					{"role": "user", "content": prompt}
				],
				temperature=temperature,
				max_tokens=max_tokens,
				stream=True,
				timeout=10,
				stream_options={"include_usage": True}
			)
			if self.cancel_event.is_set():
				print("CANCELLED")
				yield {"chunk": "[CANCELLED]"}
				return
			yield from self._process_text_stream(response, prompt)
		except Exception as e:
			self.logger.error(f"Error in generate_streamed_text: {str(e)}")
			yield {"error": f"An error occurred: {str(e)}"}
	
	def _process_json_stream(self, response):
		print(response)
		json_buffer = ""
		for chunk in response:
			if chunk.choices and chunk.choices[0].delta.content:
				msg = chunk.choices[0].delta.content
				json_buffer += msg

				if json_buffer.startswith("I'm sorry"):
					raise ValueError("I'm sorry phrase detected")
				
				while True:
					match = re.search(r'\{[^{}]*\}', json_buffer)
					if not match:
						break
					
					json_str = match.group()
					try:
						json_obj = json.loads(json_str)
						yield {"chunk": json.dumps(json_obj)}
						json_buffer = json_buffer[match.end():]
					except json.JSONDecodeError:
						break
			
			# if chunk.usage:
			# 	print("usage:", chunk.usage)
		if json_buffer.strip():
			try:
				json_obj = json.loads(json_buffer)
				yield {"chunk": json.dumps(json_obj)}
			except json.JSONDecodeError:
				pass

		yield {"chunk": "[DONE]"}
	
	def _process_text_stream(self, response, prompt):
		current_sentence = ""
		final_response = ""
		full_response = ""  # Track the complete response
		
		# Initialize usage tracking
		total_usage = {
			"completion_tokens": 0,
			"prompt_tokens": 0,
			"total_tokens": 0
		}
		
		try:
			for chunk in response:
				if self.cancel_event.is_set():
					yield {"chunk": "[CANCELLED]"}
					return

				if chunk.choices and chunk.choices[0].delta.content:
					msg = chunk.choices[0].delta.content or ""
					if len(msg) > 0:
						full_response += msg  # Accumulate the complete response

						
						# Clean the message of any potential JSON artifacts
						msg = msg.replace('}{', '} {')  # Split adjacent JSON objects
						msg = re.sub(r'}\s*{', '} {', msg)  # Handle cases with whitespace
					else:
						error_msg = (
							f"Error processing prompt: {prompt}\n"
						)
						self.logger.error(error_msg)
						self._write_error_to_file(error_msg)
						continue
						
						# Check for "I'm sorry" at the beginning of the response
					if not current_sentence and (msg.lstrip().startswith("I'm sorry") or msg.lstrip().startswith("I will not continue this story")):
						raise ValueError("I'm sorry phrase detected")
					
					current_sentence += msg
					current_sentence = current_sentence.replace("\n\n", "\\n\\n")
					
					# More robust sentence splitting
					sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', current_sentence)
					
					if len(sentences) > 1:
						complete_sentences = sentences[:-1]
						for sentence in complete_sentences:
							# Clean the sentence of any JSON-like structures
							clean_sentence = re.sub(r'[{}\[\]]', '', sentence)
							if clean_sentence.strip():
								yield {"chunk": clean_sentence.strip()}
								final_response += clean_sentence + " "
						
						current_sentence = sentences[-1]

				if chunk.usage:
					# print("usage:", chunk.usage.total_tokens)
					# Accumulate usage statistics
					total_usage["completion_tokens"] = chunk.usage.completion_tokens
					total_usage["prompt_tokens"] = chunk.usage.prompt_tokens
					total_usage["total_tokens"] = chunk.usage.total_tokens
					continue  # Skip yielding individual usage updates

			# Handle any remaining content
			if current_sentence.strip():
				clean_sentence = re.sub(r'[{}\[\]]', '', current_sentence)

				if clean_sentence.strip():
					yield {"chunk": clean_sentence.strip()}
					final_response += clean_sentence

			# Send accumulated usage stats before DONE
			if total_usage["total_tokens"] > 0:
				yield {"usage": total_usage}
			yield {"chunk": "[DONE]"}
			
		except Exception as e:
			# Log the error along with the full response
			error_msg = (
				f"Error processing stream: {str(e)}\n"
				f"Error type: {type(e).__name__}\n"
				f"Full response received:\n{full_response}\n"
				f"Current sentence buffer:\n{current_sentence}"
				f"Prompt:\n{prompt}"
			)
			# self.logger.error(error_msg)
			self._write_error_to_file(error_msg)
			# Instead of raising, we'll yield an error message
			yield {"error": f"An error occurred: {str(e)}"}
	
	def _write_error_to_file(self, error_msg):
		"""Write detailed error information to a timestamped file"""
		log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs', 'errors')
		os.makedirs(log_dir, exist_ok=True)
		
		timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
		error_file = os.path.join(log_dir, f'error_{timestamp}.log')
		
		with open(error_file, 'w') as f:
			f.write(error_msg)

	def generate_voice(
		self,
		messages: List[Dict[str, Any]],
		voice: str = "alloy",
		format: str = "wav",
		model_name: str = None,
		temperature: float = 0.7,
		max_tokens: int = 1000,
	) -> Optional[bytes]:
		"""
		Generate voice audio from text using OpenAI's audio model.
		Returns base64 decoded audio bytes.
		"""
		client, model = self._get_client_and_model(model_name)
		try:
			response = client.chat.completions.create(
				model="gpt-4o-audio-preview",  # Using the audio-capable model
				modalities=["text", "audio"],
				audio={"voice": voice, "format": format},
				messages=messages,
				temperature=temperature,
				max_tokens=max_tokens
			)
			
			# Decode the base64 audio data
			audio_bytes = base64.b64decode(response.choices[0].message.audio.data)
			return audio_bytes, response.choices[0].message.audio.id

		except Exception as e:
			self.logger.error(f"Error in generate_voice: {str(e)}")
			return None