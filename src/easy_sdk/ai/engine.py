"""
AI Analysis Engine for enhanced Django code understanding
"""

import asyncio
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import openai
except ImportError:
    openai = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from ..core.config import DjangoDocsConfig
from .prompts import PromptTemplates
from ..analyzers.model_analyzer import ModelAnalyzer
from ..analyzers.serializer_analyzer import SerializerAnalyzer
from ..analyzers.view_analyzer import ViewAnalyzer

logger = logging.getLogger(__name__)


class AIAnalysisResult:
    """Result of AI analysis operation"""
    
    def __init__(self):
        self.success = True
        self.enhanced_data: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.analysis_time = 0.0
        self.tokens_used = 0
        self.model_used = ""
    
    def add_error(self, error: str) -> None:
        """Add error to result"""
        self.errors.append(error)
        self.success = False
        logger.error(f"AI Analysis error: {error}")
    
    def add_warning(self, warning: str) -> None:
        """Add warning to result"""
        self.warnings.append(warning)
        logger.warning(f"AI Analysis warning: {warning}")


class AIAnalysisEngine:
    """
    AI-powered analysis engine that enhances structural Django analysis
    with intelligent code understanding, type inference, and documentation generation
    """
    
    def __init__(self, config: DjangoDocsConfig):
        self.config = config
        self.ai_config = config.ai
        self.prompt_templates = PromptTemplates()
        
        # Initialize enhanced analyzers
        self.model_analyzer = ModelAnalyzer(config)
        self.serializer_analyzer = SerializerAnalyzer(config)
        self.view_analyzer = ViewAnalyzer(config)
        
        # Load environment variables from .env file
        self._load_environment()
        
        # Initialize AI clients
        self.openai_client = None
        self.langchain_client = None
        self.anthropic_client = None
        
        if self.ai_config.provider == "openai":
            self._initialize_openai()
        elif self.ai_config.provider == "anthropic":
            self._initialize_anthropic()
        
        # Rate limiting
        self._request_times = []
        self._max_requests_per_minute = 50
    
    def _load_environment(self) -> None:
        """Load environment variables from .env file"""
        if load_dotenv is None:
            logger.debug("dotenv not available, skipping .env file loading")
            return
            
        # Try to find .env file in common locations
        env_paths = [
            Path.cwd() / ".env",  # Current working directory
            Path(__file__).parent.parent.parent.parent / ".env",  # Project root
            self.config.project_path / ".env",  # Django project directory
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                logger.debug(f"Loading environment from: {env_path}")
                load_dotenv(env_path)
                return
        
        logger.debug("No .env file found in common locations")
        
    def _initialize_openai(self) -> None:
        """Initialize OpenAI clients (both direct and LangChain)"""
        if openai is None or ChatOpenAI is None:
            logger.warning("OpenAI or LangChain not installed. Install with: pip install 'easy-sdk[ai]'")
            return
            
        try:
            api_key = self.ai_config.api_key or self._get_api_key_from_env("OPENAI_API_KEY")
            if api_key:
                # Initialize direct OpenAI client for Responses API
                self.openai_client = openai.OpenAI(api_key=api_key)
                
                # Initialize LangChain OpenAI client for structured interactions
                self.langchain_client = ChatOpenAI(
                    api_key=api_key,
                    model=self.ai_config.model,
                    temperature=self.ai_config.temperature,
                    max_tokens=self.ai_config.max_tokens,
                    timeout=self.ai_config.timeout
                )
                logger.info("OpenAI clients initialized (direct + LangChain)")
            else:
                logger.warning("OpenAI API key not found")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI clients: {str(e)}")
    
    def _initialize_anthropic(self) -> None:
        """Initialize Anthropic client"""
        if Anthropic is None:
            logger.warning("Anthropic not installed. Install with: pip install 'easy-sdk[ai]'")
            return
            
        try:
            api_key = self.ai_config.api_key or self._get_api_key_from_env("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = Anthropic(api_key=api_key)
                logger.info("Anthropic client initialized")
            else:
                logger.warning("Anthropic API key not found")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {str(e)}")
    
    def _get_api_key_from_env(self, env_var: str) -> Optional[str]:
        """Get API key from environment variable"""
        return os.getenv(env_var)
    
    def enhance_analysis(self, analysis_data: Dict[str, Any], progress=None, main_task=None) -> Dict[str, Any]:
        """
        Enhance structural analysis with AI insights
        
        Args:
            analysis_data: Results from Django structural analysis
            progress: Rich progress instance for updates (optional)
            main_task: Main task ID for progress updates (optional)
            
        Returns:
            Enhanced analysis data with AI insights
        """
        start_time = time.time()
        
        try:
            enhanced_data = analysis_data.copy()
            
            # Get list of apps for progress calculation
            apps_to_process = [(name, data) for name, data in analysis_data.items() if isinstance(data, dict)]
            total_apps = len(apps_to_process)
            
            # Process each app
            for i, (app_name, app_data) in enumerate(apps_to_process):
                logger.info(f"Running AI analysis for app: {app_name}")
                
                # Update progress description with current app
                if progress and main_task:
                    progress.update(
                        main_task, 
                        description=f"🧠 AI analysis: {app_name} ({i+1}/{total_apps})"
                    )
                
                enhanced_app_data = self._enhance_app_analysis(app_name, app_data)
                enhanced_data[app_name] = enhanced_app_data
            
            processing_time = time.time() - start_time
            logger.info(f"AI analysis completed in {processing_time:.2f} seconds")
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            # Return original data if AI analysis fails
            return analysis_data
    
    def _enhance_app_analysis(self, app_name: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance analysis for a single Django app"""
        enhanced_data = app_data.copy()
        
        try:
            # Enhance serializer analysis
            if 'serializers' in app_data:
                enhanced_serializers = []
                for serializer in app_data['serializers']:
                    enhanced_serializer = self._enhance_serializer_analysis(
                        app_name, serializer
                    )
                    enhanced_serializers.append(enhanced_serializer)
                enhanced_data['serializers'] = enhanced_serializers
            
            # Enhance view analysis  
            if 'views' in app_data:
                enhanced_views = []
                for view in app_data['views']:
                    enhanced_view = self._enhance_view_analysis(app_name, view)
                    enhanced_views.append(enhanced_view)
                enhanced_data['views'] = enhanced_views
            
            # Generate relationship mappings
            enhanced_data['relationships'] = self._analyze_relationships(
                app_name, enhanced_data
            )
            
        except Exception as e:
            logger.error(f"Failed to enhance analysis for app {app_name}: {str(e)}")
            # Return original data if enhancement fails
            return app_data
        
        return enhanced_data
    
    def _enhance_serializer_analysis(self, app_name: str, serializer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance serializer analysis with AI insights"""
        try:
            # Convert SerializerInfo object to dict if needed
            if hasattr(serializer_data, 'name') and not hasattr(serializer_data, 'get'):
                serializer_dict = self._convert_serializer_info_to_dict(serializer_data)
            else:
                serializer_dict = serializer_data
                
            # Prepare context for AI analysis
            context = {
                'app_name': app_name,
                'file_path': serializer_dict.get('file_path', ''),
                'serializer_code': self._extract_serializer_code(serializer_dict),
                'related_models': serializer_dict.get('related_models', [])
            }
            
            # Run AI analysis
            ai_result = self._call_ai_api(
                'SERIALIZER_ANALYSIS',
                context
            )
            
            if ai_result.success:
                # Enhance field information
                enhanced_fields = self._enhance_field_types(
                    serializer_dict.get('fields', {}),
                    ai_result.enhanced_data
                )
                
                serializer_dict['fields'] = enhanced_fields
                serializer_dict['ai_insights'] = ai_result.enhanced_data
                serializer_dict['documentation'] = ai_result.enhanced_data.get('documentation', {})
        
        except Exception as e:
            logger.warning(f"Failed to enhance serializer {serializer_dict.get('name', 'unknown')}: {str(e)}")
        
        return serializer_dict
    
    def _convert_serializer_info_to_dict(self, serializer_info) -> Dict[str, Any]:
        """Convert SerializerInfo object to dictionary format"""
        try:
            serializer_dict = {
                'name': getattr(serializer_info, 'name', ''),
                'file_path': getattr(serializer_info, 'file_path', ''),
                'fields': getattr(serializer_info, 'fields', {}),
                'related_models': getattr(serializer_info, 'related_models', []),
                'docstring': getattr(serializer_info, 'docstring', ''),
                'inheritance': getattr(serializer_info, 'inheritance', []),
                'meta_info': getattr(serializer_info, 'meta_info', {}),
            }
            return serializer_dict
        except Exception as e:
            logger.debug(f"Failed to convert SerializerInfo to dict: {e}")
            return {'name': 'unknown', 'fields': {}}

    def _convert_view_info_to_dict(self, view_info) -> Dict[str, Any]:
        """Convert ViewInfo object to dictionary format"""
        try:
            view_dict = {
                'name': getattr(view_info, 'name', ''),
                'file_path': getattr(view_info, 'file_path', ''),
                'endpoints': getattr(view_info, 'endpoints', []),
                'url_patterns': getattr(view_info, 'url_patterns', []),
                'serializer_class': getattr(view_info, 'serializer_class', []),
                'docstring': getattr(view_info, 'docstring', ''),
                'inheritance': getattr(view_info, 'inheritance', []),
                'permissions': getattr(view_info, 'permissions', []),
            }
            return view_dict
        except Exception as e:
            logger.debug(f"Failed to convert ViewInfo to dict: {e}")
            return {'name': 'unknown', 'endpoints': []}
    
    def _enhance_view_analysis(self, app_name: str, view_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance view analysis with AI insights"""
        try:
            # Convert ViewInfo object to dict if needed
            if hasattr(view_data, 'name') and not hasattr(view_data, 'get'):
                view_dict = self._convert_view_info_to_dict(view_data)
            else:
                view_dict = view_data
                
            # Prepare context for AI analysis
            context = {
                'app_name': app_name,
                'file_path': view_dict.get('file_path', ''),
                'view_code': self._extract_view_code(view_dict),
                'url_patterns': view_dict.get('url_patterns', []),
                'serializers': view_dict.get('serializer_class', [])
            }
            
            # Run AI analysis
            ai_result = self._call_ai_api(
                'VIEW_ANALYSIS',
                context
            )
            
            if ai_result.success:
                # Enhance endpoint information
                enhanced_endpoints = self._enhance_endpoints(
                    view_dict.get('endpoints', []),
                    ai_result.enhanced_data
                )
                
                view_dict['endpoints'] = enhanced_endpoints
                view_dict['ai_insights'] = ai_result.enhanced_data
                view_dict['documentation'] = ai_result.enhanced_data.get('documentation', {})
        
        except Exception as e:
            logger.warning(f"Failed to enhance view {view_dict.get('name', 'unknown')}: {str(e)}")
        
        return view_dict
    
    def _enhance_field_types(self, fields: Dict[str, Any], ai_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance field type information with AI analysis"""
        enhanced_fields = fields.copy()
        
        try:
            ai_field_analysis = ai_insights.get('field_analysis', {})
            
            for field_name, field_data in enhanced_fields.items():
                if field_name in ai_field_analysis:
                    ai_field_info = ai_field_analysis[field_name]
                    
                    # Enhance field properties
                    field_data.update({
                        'ai_inferred_type': ai_field_info.get('data_type'),
                        'ai_description': ai_field_info.get('description'),
                        'ai_validation_rules': ai_field_info.get('validation_rules', []),
                        'ai_examples': ai_field_info.get('examples', []),
                        'business_purpose': ai_field_info.get('business_purpose', ''),
                    })
                    
                    # Generate TypeScript type
                    ts_type = self._generate_typescript_type(field_data, ai_field_info)
                    field_data['typescript_type'] = ts_type
        
        except Exception as e:
            logger.warning(f"Failed to enhance field types: {str(e)}")
        
        return enhanced_fields
    
    def _enhance_endpoints(self, endpoints: List[Dict[str, Any]], ai_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhance endpoint information with AI analysis"""
        enhanced_endpoints = []
        
        try:
            ai_endpoint_analysis = ai_insights.get('endpoint_mapping', {})
            
            for endpoint in endpoints:
                enhanced_endpoint = endpoint.copy()
                endpoint_key = f"{endpoint['method']} {endpoint['path']}"
                
                if endpoint_key in ai_endpoint_analysis:
                    ai_endpoint_info = ai_endpoint_analysis[endpoint_key]
                    
                    enhanced_endpoint.update({
                        'ai_description': ai_endpoint_info.get('description'),
                        'ai_examples': ai_endpoint_info.get('examples', {}),
                        'ai_parameters': ai_endpoint_info.get('parameters', []),
                        'ai_responses': ai_endpoint_info.get('responses', {}),
                        'business_logic': ai_endpoint_info.get('business_logic', ''),
                    })
                
                enhanced_endpoints.append(enhanced_endpoint)
        
        except Exception as e:
            logger.warning(f"Failed to enhance endpoints: {str(e)}")
            return endpoints
        
        return enhanced_endpoints
    
    def _generate_typescript_type(self, field_data: Dict[str, Any], ai_field_info: Dict[str, Any]) -> str:
        """Generate TypeScript type for a field"""
        try:
            context = {
                'field_name': field_data.get('name', ''),
                'field_type': field_data.get('type', ''),
                'field_options': field_data,
                'context': ai_field_info
            }
            
            ai_result = self._call_ai_api(
                'TYPE_INFERENCE',
                context
            )
            
            if ai_result.success and 'typescript_type' in ai_result.enhanced_data:
                return ai_result.enhanced_data['typescript_type']
        
        except Exception as e:
            logger.warning(f"Failed to generate TypeScript type: {str(e)}")
        
        # Fallback to basic type mapping
        return self._basic_typescript_mapping(field_data.get('type', 'any'))
    
    def _basic_typescript_mapping(self, django_type: str) -> str:
        """Basic Django to TypeScript type mapping"""
        mapping = {
            'string': 'string',
            'integer': 'number',
            'float': 'number',
            'decimal': 'number',
            'boolean': 'boolean',
            'date': 'string',
            'datetime': 'string',
            'time': 'string',
            'email': 'string',
            'url': 'string',
            'uuid': 'string',
            'json': 'object',
            'list': 'any[]',
            'object': 'object',
        }
        
        return mapping.get(django_type, 'any')
    
    def _analyze_relationships(self, app_name: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationships between components"""
        try:
            context = {
                'components': json.dumps(app_data, indent=2)
            }
            
            ai_result = self._call_ai_api(
                'RELATIONSHIP_MAPPING',
                context
            )
            
            if ai_result.success:
                return ai_result.enhanced_data
        
        except Exception as e:
            logger.warning(f"Failed to analyze relationships for app {app_name}: {str(e)}")
        
        return {}
    
    def _call_ai_api(self, template_name: str, context: Dict[str, Any]) -> AIAnalysisResult:
        """Call AI API with rate limiting and error handling"""
        result = AIAnalysisResult()
        
        try:
            # Apply rate limiting
            self._apply_rate_limiting()
            
            # Prepare prompt
            prompt = self.prompt_templates.get_prompt(template_name, **context)
            
            # Enhanced logging for AI calls
            app_name = context.get('app_name', 'unknown')
            context_info = f"app={app_name}"
            if 'serializer_name' in context:
                context_info += f", serializer={context['serializer_name']}"
            elif 'view_name' in context:
                context_info += f", view={context['view_name']}"
            
            logger.info(f"🤖 AI Call: {template_name} ({context_info}) -> {self.ai_config.provider}:{self.ai_config.model}")
            if self.config.verbose:
                logger.debug(f"AI Prompt length: {len(prompt)} chars")
                logger.debug(f"AI Context keys: {list(context.keys())}")
            
            # Call appropriate AI service
            start_time = time.time()
            if self.ai_config.provider == "openai" and self.openai_client:
                response = self._call_openai(prompt)
            elif self.ai_config.provider == "anthropic" and self.anthropic_client:
                response = self._call_anthropic(prompt)
            else:
                result.add_error("No AI provider configured or available")
                logger.warning(f"❌ AI Call failed: No provider configured (requested: {self.ai_config.provider})")
                return result
            
            call_duration = time.time() - start_time
            
            # Parse response
            result.enhanced_data = self._parse_ai_response(response)
            result.model_used = self.ai_config.model
            
            # Log success with timing
            response_length = len(response) if response else 0
            logger.info(f"✅ AI Response: {template_name} completed in {call_duration:.2f}s ({response_length} chars)")
            
        except Exception as e:
            logger.error(f"❌ AI Call failed: {template_name} - {str(e)}")
            result.add_error(f"AI API call failed: {str(e)}")
        
        return result
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI Responses API"""
        try:
            # Try using the new Responses API first
            response = self.openai_client.responses.create(
                model=self.ai_config.model,
                instructions="You are an expert Django developer and technical writer. Analyze the provided code and generate comprehensive, accurate documentation.",
                input=prompt,
                max_output_tokens=self.ai_config.max_tokens,
                temperature=self.ai_config.temperature,
                text={"format": {"type": "text"}},
                store=True  # Store for better caching and optimization
            )
            
            # Extract text from the new response format
            if response.output and len(response.output) > 0:
                first_output = response.output[0]
                if hasattr(first_output, 'content') and len(first_output.content) > 0:
                    first_content = first_output.content[0]
                    if hasattr(first_content, 'text'):
                        return first_content.text
            
            # Fallback to empty string if parsing fails
            logger.warning("Could not extract text from Responses API response")
            return ""
            
        except Exception as e:
            # Fallback to LangChain client if Responses API fails
            logger.debug(f"Responses API failed, falling back to LangChain: {str(e)}")
            if self.langchain_client:
                from langchain_core.messages import HumanMessage, SystemMessage
                
                messages = [
                    SystemMessage(content="You are an expert Django developer and technical writer. Analyze the provided code and generate comprehensive, accurate documentation."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.langchain_client.invoke(messages)
                return response.content
            else:
                raise Exception(f"Both Responses API and LangChain failed: {str(e)}")
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        response = self.anthropic_client.messages.create(
            model=self.ai_config.model,
            max_tokens=self.ai_config.max_tokens,
            temperature=self.ai_config.temperature,
            system="You are an expert Django developer and technical writer. Analyze the provided code and generate comprehensive, accurate documentation.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        try:
            # Try to extract JSON from response if present
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Otherwise, return response as structured text analysis
            return {
                'raw_response': response,
                'analysis_sections': self._extract_sections(response)
            }
        
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {str(e)}")
            return {'raw_response': response}
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract sections from markdown-like text"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in text.split('\n'):
            if line.startswith('##'):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.replace('##', '').strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _apply_rate_limiting(self) -> None:
        """Apply rate limiting to AI API calls"""
        now = time.time()
        
        # Remove requests older than 1 minute
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        # Check if we're at the limit
        if len(self._request_times) >= self._max_requests_per_minute:
            sleep_time = 60 - (now - self._request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limiting: sleeping for {sleep_time:.1f} seconds")
                time.sleep(sleep_time)
        
        self._request_times.append(now)
    
    def _extract_serializer_code(self, serializer_data: Dict[str, Any]) -> str:
        """Extract serializer code from file for AI analysis"""
        try:
            file_path = serializer_data.get('file_path')
            if not file_path:
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract just the serializer class (simplified)
            class_name = serializer_data.get('name', '')
            if class_name:
                # Simple extraction - could be enhanced with AST parsing
                class_start = content.find(f"class {class_name}")
                if class_start != -1:
                    # Find the end of the class (next class or end of file)
                    next_class = content.find("\nclass ", class_start + 1)
                    if next_class != -1:
                        return content[class_start:next_class]
                    else:
                        return content[class_start:]
            
            return content[:2000]  # Limit to avoid token limits
            
        except Exception as e:
            logger.warning(f"Failed to extract serializer code: {str(e)}")
            return ""
    
    def _extract_view_code(self, view_data: Dict[str, Any]) -> str:
        """Extract view code from file for AI analysis"""
        try:
            file_path = view_data.get('file_path')
            if not file_path:
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract just the view class (simplified)
            class_name = view_data.get('name', '')
            if class_name:
                class_start = content.find(f"class {class_name}")
                if class_start != -1:
                    next_class = content.find("\nclass ", class_start + 1)
                    if next_class != -1:
                        return content[class_start:next_class]
                    else:
                        return content[class_start:]
            
            return content[:2000]  # Limit to avoid token limits
            
        except Exception as e:
            logger.warning(f"Failed to extract view code: {str(e)}")
            return ""
    
    def analyze_api_structure(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze API structure and extract patterns for SDK generation
        
        Args:
            analysis_result: Complete Django analysis results
            
        Returns:
            Structured API analysis with patterns and SDK generation insights
        """
        try:
            logger.info("🧠 AI analyzing API structure for SDK generation")
            
            # Prepare context for AI analysis
            context = {
                'total_apps': len(analysis_result),
                'app_names': list(analysis_result.keys()),
                'structure_data': json.dumps(analysis_result, indent=2, default=str)[:8000]  # Limit size
            }
            
            # Call AI to analyze overall structure
            ai_result = self._call_ai_api('API_STRUCTURE_ANALYSIS', context)
            
            if ai_result.success:
                structure_analysis = ai_result.enhanced_data
            else:
                # Fallback to basic analysis
                structure_analysis = self._basic_structure_analysis(analysis_result)
            
            # Enhance with additional insights
            structure_analysis.update({
                'total_apps': len(analysis_result),
                'generated_at': time.time(),
                'sdk_recommendations': self._generate_sdk_recommendations(analysis_result, structure_analysis)
            })
            
            logger.info(f"✅ API structure analysis completed with {len(structure_analysis.get('common_patterns', []))} patterns identified")
            return structure_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze API structure: {str(e)}")
            return self._basic_structure_analysis(analysis_result)
    
    def comprehensive_analysis(self, analysis_data: Dict[str, Any], progress=None, main_task=None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis using enhanced analyzers and AI insights
        
        Args:
            analysis_data: Results from Django structural analysis
            progress: Rich progress instance for updates (optional)
            main_task: Main task ID for progress updates (optional)
            
        Returns:
            Enhanced analysis data with comprehensive insights
        """
        start_time = time.time()
        
        try:
            enhanced_data = analysis_data.copy()
            
            # Get list of apps for progress calculation
            apps_to_process = [(name, data) for name, data in analysis_data.items() if isinstance(data, dict)]
            total_apps = len(apps_to_process)
            
            # Process each app with enhanced analysis
            for i, (app_name, app_data) in enumerate(apps_to_process):
                logger.info(f"Running comprehensive analysis for app: {app_name}")
                
                # Update progress description with current app
                if progress and main_task:
                    progress.update(
                        main_task, 
                        description=f"🔍 Comprehensive analysis: {app_name} ({i+1}/{total_apps})"
                    )
                
                enhanced_app_data = self._comprehensive_app_analysis(app_name, app_data)
                enhanced_data[app_name] = enhanced_app_data
            
            # Generate overall API insights
            enhanced_data['_api_insights'] = self._generate_api_insights(enhanced_data)
            
            processing_time = time.time() - start_time
            logger.info(f"Comprehensive analysis completed in {processing_time:.2f} seconds")
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {str(e)}")
            # Return original data if analysis fails
            return analysis_data
    
    def _comprehensive_app_analysis(self, app_name: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive analysis for a single Django app"""
        enhanced_data = app_data.copy()
        
        try:
            # Enhance models analysis
            if 'models' in app_data:
                enhanced_models = []
                model_files = app_data['models']
                for model_file in model_files:
                    file_models = self.model_analyzer.analyze_model_file(Path(model_file))
                    for model in file_models:
                        # Add AI insights to each model
                        enhanced_model = self._enhance_model_analysis(app_name, model)
                        enhanced_models.append(enhanced_model)
                enhanced_data['models'] = enhanced_models
                
                # Add model relationships and dependencies
                if enhanced_models:
                    enhanced_data['model_relationships'] = self.model_analyzer.extract_model_relationships(enhanced_models)
                    enhanced_data['model_dependencies'] = self.model_analyzer.get_model_dependencies(enhanced_models)
            
            # Enhance serializers analysis with detailed schemas
            if 'serializers' in app_data:
                enhanced_serializers = []
                serializer_files = app_data['serializers']
                for serializer_file in serializer_files:
                    file_serializers = self.serializer_analyzer.analyze_serializer_file(Path(serializer_file))
                    for serializer in file_serializers:
                        enhanced_serializer = self._enhance_serializer_analysis(app_name, serializer)
                        enhanced_serializers.append(enhanced_serializer)
                enhanced_data['serializers'] = enhanced_serializers
                
                # Add serializer schemas and examples
                if enhanced_serializers:
                    enhanced_data['serializer_schemas'] = self.serializer_analyzer.extract_input_output_schemas(enhanced_serializers)
                    enhanced_data['serializer_examples'] = {}
                    for serializer in enhanced_serializers:
                        enhanced_data['serializer_examples'][serializer.name] = self.serializer_analyzer.generate_serializer_examples(serializer)
            
            # Enhance views analysis with detailed endpoint information
            if 'views' in app_data:
                enhanced_views = []
                view_files = app_data['views']
                for view_file in view_files:
                    file_views = self.view_analyzer.analyze_view_file(Path(view_file))
                    for view in file_views:
                        enhanced_view = self._enhance_view_analysis(app_name, view)
                        enhanced_views.append(enhanced_view)
                enhanced_data['views'] = enhanced_views
                
                # Add endpoint schemas and examples
                if enhanced_views:
                    enhanced_data['endpoint_schemas'] = self.view_analyzer.extract_endpoint_schemas(enhanced_views)
                    enhanced_data['endpoint_examples'] = {}
                    for view in enhanced_views:
                        enhanced_data['endpoint_examples'][view.name] = self.view_analyzer.generate_endpoint_examples(view)
            
            # Generate cross-component relationships
            enhanced_data['component_relationships'] = self._analyze_component_relationships(
                app_name, enhanced_data
            )
            
        except Exception as e:
            logger.error(f"Failed to perform comprehensive analysis for app {app_name}: {str(e)}")
            # Return original data if enhancement fails
            return app_data
        
        return enhanced_data
    
    def _enhance_model_analysis(self, app_name: str, model_info) -> Dict[str, Any]:
        """Enhance model analysis with AI insights"""
        try:
            # Convert model info to dict if needed
            if hasattr(model_info, 'to_dict'):
                model_dict = model_info.to_dict()
            else:
                model_dict = model_info
                
            # Prepare context for AI analysis
            context = {
                'app_name': app_name,
                'model_name': model_dict.get('name', ''),
                'file_path': model_dict.get('file_path', ''),
                'model_code': self._extract_model_code(model_dict),
                'fields': model_dict.get('fields', {}),
                'relationships': model_dict.get('related_models', [])
            }
            
            # Run AI analysis
            ai_result = self._call_ai_api('MODEL_ANALYSIS', context)
            
            if ai_result.success:
                # Enhance field information with AI insights
                enhanced_fields = self._enhance_model_fields(
                    model_dict.get('fields', {}),
                    ai_result.enhanced_data
                )
                
                model_dict['fields'] = enhanced_fields
                model_dict['ai_insights'] = ai_result.enhanced_data
                model_dict['business_purpose'] = ai_result.enhanced_data.get('business_purpose', '')
                model_dict['usage_patterns'] = ai_result.enhanced_data.get('usage_patterns', [])
        
        except Exception as e:
            logger.warning(f"Failed to enhance model {model_dict.get('name', 'unknown')}: {str(e)}")
        
        return model_dict
    
    def _enhance_model_fields(self, fields: Dict[str, Any], ai_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance model field information with AI analysis"""
        enhanced_fields = {}
        
        try:
            ai_field_analysis = ai_insights.get('field_analysis', {})
            
            for field_name, field_data in fields.items():
                enhanced_field = field_data.copy() if isinstance(field_data, dict) else field_data
                
                if field_name in ai_field_analysis:
                    ai_field_info = ai_field_analysis[field_name]
                    
                    if isinstance(enhanced_field, dict):
                        # Enhance field properties
                        enhanced_field.update({
                            'ai_description': ai_field_info.get('description'),
                            'business_purpose': ai_field_info.get('business_purpose', ''),
                            'usage_examples': ai_field_info.get('examples', []),
                            'validation_rationale': ai_field_info.get('validation_rationale', ''),
                            'api_documentation': ai_field_info.get('api_docs', '')
                        })
                        
                        # Generate OpenAPI schema
                        enhanced_field['openapi_schema'] = self._generate_field_openapi_schema(enhanced_field, ai_field_info)
                
                enhanced_fields[field_name] = enhanced_field
        
        except Exception as e:
            logger.warning(f"Failed to enhance model fields: {str(e)}")
            return fields
        
        return enhanced_fields
    
    def _generate_field_openapi_schema(self, field_data: Dict[str, Any], ai_field_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OpenAPI schema for a model field"""
        schema = {
            'type': self._map_django_field_to_openapi_type(field_data.get('type', 'string')),
            'description': ai_field_info.get('description', field_data.get('help_text', ''))
        }
        
        # Add constraints
        if field_data.get('null'):
            schema['nullable'] = True
        if field_data.get('max_length'):
            schema['maxLength'] = field_data['max_length']
        if field_data.get('choices'):
            schema['enum'] = [choice[0] if isinstance(choice, tuple) else choice for choice in field_data['choices']]
        if field_data.get('default') is not None:
            schema['default'] = field_data['default']
        
        # Add format for specific types
        field_type = field_data.get('type', '')
        if field_type == 'date':
            schema['format'] = 'date'
        elif field_type == 'datetime':
            schema['format'] = 'date-time'
        elif field_type == 'email':
            schema['format'] = 'email'
        elif field_type == 'url':
            schema['format'] = 'uri'
        elif field_type == 'uuid':
            schema['format'] = 'uuid'
        
        return schema
    
    def _map_django_field_to_openapi_type(self, django_type: str) -> str:
        """Map Django field types to OpenAPI types"""
        type_mapping = {
            'auto': 'integer',
            'big_auto': 'integer',
            'big_integer': 'integer',
            'binary': 'string',
            'boolean': 'boolean',
            'string': 'string',
            'date': 'string',
            'datetime': 'string',
            'decimal': 'number',
            'duration': 'string',
            'email': 'string',
            'file': 'string',
            'file_path': 'string',
            'float': 'number',
            'image': 'string',
            'integer': 'integer',
            'ip_address': 'string',
            'json': 'object',
            'positive_integer': 'integer',
            'positive_small_integer': 'integer',
            'slug': 'string',
            'small_integer': 'integer',
            'text': 'string',
            'time': 'string',
            'url': 'string',
            'uuid': 'string',
            'foreign_key': 'integer',
            'many_to_many': 'array',
            'one_to_one': 'integer',
        }
        return type_mapping.get(django_type, 'string')
    
    def _analyze_component_relationships(self, app_name: str, app_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze relationships between models, serializers, and views"""
        try:
            context = {
                'app_name': app_name,
                'models': app_data.get('models', []),
                'serializers': app_data.get('serializers', []),
                'views': app_data.get('views', []),
                'component_data': json.dumps(app_data, indent=2, default=str)[:8000]  # Limit size
            }
            
            ai_result = self._call_ai_api('COMPONENT_RELATIONSHIP_ANALYSIS', context)
            
            if ai_result.success:
                return ai_result.enhanced_data
        
        except Exception as e:
            logger.warning(f"Failed to analyze component relationships for app {app_name}: {str(e)}")
        
        return {}
    
    def _generate_api_insights(self, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall API insights and recommendations"""
        try:
            # Collect statistics
            total_models = 0
            total_serializers = 0
            total_views = 0
            total_endpoints = 0
            
            for app_name, app_data in enhanced_data.items():
                if isinstance(app_data, dict) and not app_name.startswith('_'):
                    total_models += len(app_data.get('models', []))
                    total_serializers += len(app_data.get('serializers', []))
                    total_views += len(app_data.get('views', []))
                    
                    # Count endpoints
                    for view in app_data.get('views', []):
                        if hasattr(view, 'endpoints'):
                            total_endpoints += len(view.endpoints)
                        elif isinstance(view, dict):
                            total_endpoints += len(view.get('endpoints', []))
            
            context = {
                'total_models': total_models,
                'total_serializers': total_serializers,
                'total_views': total_views,
                'total_endpoints': total_endpoints,
                'apps': list(enhanced_data.keys()),
                'api_structure': json.dumps(enhanced_data, indent=2, default=str)[:10000]  # Limit size
            }
            
            ai_result = self._call_ai_api('API_INSIGHTS_GENERATION', context)
            
            if ai_result.success:
                insights = ai_result.enhanced_data
            else:
                # Fallback to basic insights
                insights = self._generate_basic_api_insights(enhanced_data)
            
            # Add statistics
            insights.update({
                'statistics': {
                    'total_models': total_models,
                    'total_serializers': total_serializers,
                    'total_views': total_views,
                    'total_endpoints': total_endpoints,
                    'total_apps': len([k for k in enhanced_data.keys() if not k.startswith('_')])
                },
                'generated_at': time.time()
            })
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate API insights: {str(e)}")
            return self._generate_basic_api_insights(enhanced_data)
    
    def _generate_basic_api_insights(self, enhanced_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic API insights without AI"""
        return {
            'complexity_assessment': 'moderate',
            'architectural_patterns': ['REST', 'Django REST Framework'],
            'recommendations': [
                'API follows Django REST Framework conventions',
                'Consider adding comprehensive documentation',
                'Implement proper error handling'
            ],
            'security_considerations': [
                'Ensure proper authentication on all endpoints',
                'Validate all input data',
                'Implement rate limiting'
            ]
        }
    
    def _extract_model_code(self, model_data: Dict[str, Any]) -> str:
        """Extract model code from file for AI analysis"""
        try:
            file_path = model_data.get('file_path')
            if not file_path:
                return ""
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract just the model class (simplified)
            class_name = model_data.get('name', '')
            if class_name:
                # Simple extraction - could be enhanced with AST parsing
                class_start = content.find(f"class {class_name}")
                if class_start != -1:
                    # Find the end of the class (next class or end of file)
                    next_class = content.find("\nclass ", class_start + 1)
                    if next_class != -1:
                        return content[class_start:next_class]
                    else:
                        return content[class_start:]
            
            return content[:2000]  # Limit to avoid token limits
            
        except Exception as e:
            logger.warning(f"Failed to extract model code: {str(e)}")
            return ""
    
    def _basic_structure_analysis(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback basic structure analysis without AI"""
        try:
            all_endpoints = []
            all_serializers = []
            
            # Collect all endpoints and serializers
            for app_name, app_data in analysis_result.items():
                if isinstance(app_data, dict):
                    # Collect endpoints
                    for view in app_data.get('views', []):
                        view_data = view if isinstance(view, dict) else {
                            'endpoints': getattr(view, 'endpoints', [])
                        }
                        all_endpoints.extend(view_data.get('endpoints', []))
                    
                    # Collect serializers
                    all_serializers.extend(app_data.get('serializers', []))
            
            # Analyze patterns
            common_patterns = []
            
            # HTTP methods used
            methods = set()
            for endpoint in all_endpoints:
                method = endpoint.get('method', 'GET') if isinstance(endpoint, dict) else getattr(endpoint, 'method', 'GET')
                methods.add(method)
            if methods:
                common_patterns.append(f"HTTP methods: {', '.join(sorted(methods))}")
            
            # Authentication strategy (basic detection)
            auth_strategy = 'token'  # Default assumption for Django REST
            
            # URL patterns
            base_url_pattern = '/api'  # Common Django pattern
            
            # Pagination strategy
            pagination_strategy = 'page_number'  # Django default
            
            return {
                'common_patterns': common_patterns,
                'auth_strategy': auth_strategy,
                'base_url_pattern': base_url_pattern,
                'error_handling': {
                    'standard_codes': [400, 401, 403, 404, 500],
                    'format': 'json'
                },
                'pagination_strategy': pagination_strategy,
                'total_endpoints': len(all_endpoints),
                'total_serializers': len(all_serializers)
            }
            
        except Exception as e:
            logger.warning(f"Basic structure analysis failed: {str(e)}")
            return {
                'common_patterns': [],
                'auth_strategy': 'token',
                'base_url_pattern': '/api',
                'error_handling': {},
                'pagination_strategy': 'page_number'
            }
    
    def _generate_sdk_recommendations(self, analysis_result: Dict[str, Any], structure_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations for SDK structure"""
        try:
            recommendations = {
                'client_structure': 'multi_client',  # One client per app
                'async_support': True,
                'retry_logic': True,
                'rate_limiting': False,  # Only if detected
                'caching': False,
                'validation': True,
                'type_hints': True
            }
            
            # Analyze complexity to determine recommendations
            total_apps = len(analysis_result)
            total_endpoints = sum(
                len(app_data.get('views', [])) 
                for app_data in analysis_result.values() 
                if isinstance(app_data, dict)
            )
            
            if total_apps > 5 or total_endpoints > 20:
                recommendations['modular_structure'] = True
                recommendations['async_support'] = True
            
            if structure_analysis.get('auth_strategy') in ['oauth', 'jwt']:
                recommendations['token_refresh'] = True
            
            return recommendations
            
        except Exception as e:
            logger.warning(f"Failed to generate SDK recommendations: {str(e)}")
            return {
                'client_structure': 'single_client',
                'async_support': False,
                'validation': True
            }