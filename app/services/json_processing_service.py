"""
JSON Processing Service.
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
import asyncio

from app.core.config import settings
from app.core.logging import get_logger
from app.models.schemas import JSONProcessingRequest, JSONProcessingResponse

logger = get_logger(__name__)


class JSONProcessingService:
    """
    Service for processing JSON data with various scripts.
    """
    
    def __init__(self):
        self.scripts_dir = "app/scripts"
        self.available_scripts = {}
        self.is_initialized = False
        
    async def initialize(self):
        """
        Initialize the JSON processing service.
        """
        try:
            logger.info("Initializing JSON processing service...")
            
            # Create scripts directory if it doesn't exist
            if not os.path.exists(self.scripts_dir):
                os.makedirs(self.scripts_dir)
            
            # Load available scripts
            await self._load_scripts()
            
            self.is_initialized = True
            logger.info("JSON processing service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize JSON processing service: {e}")
            raise
    
    async def _load_scripts(self):
        """
        Load available processing scripts.
        """
        # Define built-in scripts
        self.available_scripts = {
            'data_cleaner': self._clean_data,
            'data_validator': self._validate_data,
            'data_transformer': self._transform_data,
            'data_aggregator': self._aggregate_data,
            'data_filter': self._filter_data,
            'data_enricher': self._enrich_data,
        }
        
        logger.info(f"Loaded {len(self.available_scripts)} processing scripts")
    
    async def process_json(self, request: JSONProcessingRequest) -> JSONProcessingResponse:
        """
        Process JSON data using specified script.
        """
        if not self.is_initialized:
            raise RuntimeError("JSON processing service not initialized")
        
        start_time = time.time()
        
        try:
            # Determine script to use
            script_name = request.script_name or 'data_cleaner'
            
            if script_name not in self.available_scripts:
                raise ValueError(f"Script '{script_name}' not found")
            
            # Get processing function
            processing_func = self.available_scripts[script_name]
            
            # Process data
            processed_data = await processing_func(request.data, request.options)
            
            processing_time = time.time() - start_time
            
            return JSONProcessingResponse(
                processed_data=processed_data,
                script_used=script_name,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"JSON processing failed: {e}")
            raise
    
    async def _clean_data(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean JSON data by removing null values, duplicates, etc.
        """
        try:
            # Remove null values
            remove_nulls = options.get('remove_nulls', True)
            remove_empty_strings = options.get('remove_empty_strings', True)
            
            def clean_dict(d):
                if isinstance(d, dict):
                    cleaned = {}
                    for k, v in d.items():
                        if remove_nulls and v is None:
                            continue
                        if remove_empty_strings and v == "":
                            continue
                        if isinstance(v, (dict, list)):
                            cleaned[k] = clean_dict(v)
                        else:
                            cleaned[k] = v
                    return cleaned
                elif isinstance(d, list):
                    return [clean_dict(item) for item in d if item is not None]
                else:
                    return d
            
            cleaned_data = clean_dict(data)
            
            return {
                'cleaned_data': cleaned_data,
                'original_keys': len(data) if isinstance(data, dict) else 0,
                'cleaned_keys': len(cleaned_data) if isinstance(cleaned_data, dict) else 0,
                'cleaning_options': options
            }
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            raise
    
    async def _validate_data(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON data structure and content.
        """
        try:
            validation_errors = []
            validation_warnings = []
            
            # Required fields validation
            required_fields = options.get('required_fields', [])
            for field in required_fields:
                if field not in data:
                    validation_errors.append(f"Missing required field: {field}")
            
            # Data type validation
            field_types = options.get('field_types', {})
            for field, expected_type in field_types.items():
                if field in data:
                    value = data[field]
                    if not isinstance(value, expected_type):
                        validation_errors.append(
                            f"Field '{field}' expected type {expected_type.__name__}, got {type(value).__name__}"
                        )
            
            # Value range validation
            value_ranges = options.get('value_ranges', {})
            for field, (min_val, max_val) in value_ranges.items():
                if field in data:
                    value = data[field]
                    if isinstance(value, (int, float)):
                        if value < min_val or value > max_val:
                            validation_errors.append(
                                f"Field '{field}' value {value} not in range [{min_val}, {max_val}]"
                            )
            
            # Check for deprecated fields
            deprecated_fields = options.get('deprecated_fields', [])
            for field in deprecated_fields:
                if field in data:
                    validation_warnings.append(f"Deprecated field used: {field}")
            
            is_valid = len(validation_errors) == 0
            
            return {
                'is_valid': is_valid,
                'validation_errors': validation_errors,
                'validation_warnings': validation_warnings,
                'validated_data': data,
                'validation_summary': {
                    'total_fields': len(data) if isinstance(data, dict) else 0,
                    'error_count': len(validation_errors),
                    'warning_count': len(validation_warnings)
                }
            }
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            raise
    
    async def _transform_data(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform JSON data structure.
        """
        try:
            transformed_data = data.copy()
            
            # Field mapping
            field_mapping = options.get('field_mapping', {})
            for old_field, new_field in field_mapping.items():
                if old_field in transformed_data:
                    transformed_data[new_field] = transformed_data.pop(old_field)
            
            # Value transformations
            value_transformations = options.get('value_transformations', {})
            for field, transform_func in value_transformations.items():
                if field in transformed_data:
                    if transform_func == 'upper':
                        transformed_data[field] = str(transformed_data[field]).upper()
                    elif transform_func == 'lower':
                        transformed_data[field] = str(transformed_data[field]).lower()
                    elif transform_func == 'capitalize':
                        transformed_data[field] = str(transformed_data[field]).capitalize()
                    elif transform_func == 'strip':
                        transformed_data[field] = str(transformed_data[field]).strip()
            
            # Add computed fields
            computed_fields = options.get('computed_fields', {})
            for field, computation in computed_fields.items():
                if computation == 'timestamp':
                    transformed_data[field] = datetime.now().isoformat()
                elif computation == 'data_hash':
                    transformed_data[field] = hash(str(data))
            
            return {
                'transformed_data': transformed_data,
                'transformation_summary': {
                    'original_fields': len(data) if isinstance(data, dict) else 0,
                    'transformed_fields': len(transformed_data) if isinstance(transformed_data, dict) else 0,
                    'applied_transformations': len(field_mapping) + len(value_transformations) + len(computed_fields)
                }
            }
            
        except Exception as e:
            logger.error(f"Data transformation failed: {e}")
            raise
    
    async def _aggregate_data(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate JSON data.
        """
        try:
            # Handle list of records
            if isinstance(data, dict) and 'records' in data:
                records = data['records']
            elif isinstance(data, list):
                records = data
            else:
                records = [data]
            
            if not records:
                return {'aggregated_data': {}, 'record_count': 0}
            
            # Group by field
            group_by = options.get('group_by')
            aggregations = options.get('aggregations', {})
            
            if group_by:
                # Group records by field
                groups = {}
                for record in records:
                    if isinstance(record, dict) and group_by in record:
                        group_key = record[group_by]
                        if group_key not in groups:
                            groups[group_key] = []
                        groups[group_key].append(record)
                
                # Apply aggregations to each group
                aggregated_data = {}
                for group_key, group_records in groups.items():
                    group_agg = {'count': len(group_records)}
                    
                    for field, agg_func in aggregations.items():
                        values = [r.get(field) for r in group_records if field in r and r[field] is not None]
                        if values:
                            if agg_func == 'sum':
                                group_agg[f'{field}_sum'] = sum(values)
                            elif agg_func == 'avg':
                                group_agg[f'{field}_avg'] = sum(values) / len(values)
                            elif agg_func == 'min':
                                group_agg[f'{field}_min'] = min(values)
                            elif agg_func == 'max':
                                group_agg[f'{field}_max'] = max(values)
                    
                    aggregated_data[group_key] = group_agg
            else:
                # Global aggregation
                aggregated_data = {'count': len(records)}
                
                for field, agg_func in aggregations.items():
                    values = [r.get(field) for r in records if isinstance(r, dict) and field in r and r[field] is not None]
                    if values:
                        if agg_func == 'sum':
                            aggregated_data[f'{field}_sum'] = sum(values)
                        elif agg_func == 'avg':
                            aggregated_data[f'{field}_avg'] = sum(values) / len(values)
                        elif agg_func == 'min':
                            aggregated_data[f'{field}_min'] = min(values)
                        elif agg_func == 'max':
                            aggregated_data[f'{field}_max'] = max(values)
            
            return {
                'aggregated_data': aggregated_data,
                'record_count': len(records),
                'aggregation_summary': {
                    'group_by': group_by,
                    'aggregations_applied': len(aggregations)
                }
            }
            
        except Exception as e:
            logger.error(f"Data aggregation failed: {e}")
            raise
    
    async def _filter_data(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter JSON data based on criteria.
        """
        try:
            filters = options.get('filters', {})
            
            # Handle list of records
            if isinstance(data, dict) and 'records' in data:
                records = data['records']
            elif isinstance(data, list):
                records = data
            else:
                records = [data]
            
            filtered_records = []
            
            for record in records:
                if not isinstance(record, dict):
                    continue
                
                include_record = True
                
                for field, criteria in filters.items():
                    if field not in record:
                        include_record = False
                        break
                    
                    value = record[field]
                    
                    if isinstance(criteria, dict):
                        # Complex criteria
                        if 'equals' in criteria and value != criteria['equals']:
                            include_record = False
                            break
                        if 'not_equals' in criteria and value == criteria['not_equals']:
                            include_record = False
                            break
                        if 'greater_than' in criteria and value <= criteria['greater_than']:
                            include_record = False
                            break
                        if 'less_than' in criteria and value >= criteria['less_than']:
                            include_record = False
                            break
                        if 'contains' in criteria and criteria['contains'] not in str(value):
                            include_record = False
                            break
                    else:
                        # Simple equality
                        if value != criteria:
                            include_record = False
                            break
                
                if include_record:
                    filtered_records.append(record)
            
            return {
                'filtered_data': filtered_records,
                'original_count': len(records),
                'filtered_count': len(filtered_records),
                'filters_applied': filters
            }
            
        except Exception as e:
            logger.error(f"Data filtering failed: {e}")
            raise
    
    async def _enrich_data(self, data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich JSON data with additional information.
        """
        try:
            enriched_data = data.copy()
            
            # Add metadata
            add_metadata = options.get('add_metadata', True)
            if add_metadata:
                enriched_data['_metadata'] = {
                    'processed_at': datetime.now().isoformat(),
                    'processing_service': 'JSON Processing Service',
                    'enrichment_version': '1.0.0'
                }
            
            # Add computed fields
            computed_fields = options.get('computed_fields', {})
            for field, computation in computed_fields.items():
                if computation == 'record_id':
                    enriched_data[field] = f"record_{hash(str(data)) % 1000000}"
                elif computation == 'data_size':
                    enriched_data[field] = len(str(data))
                elif computation == 'field_count':
                    enriched_data[field] = len(data) if isinstance(data, dict) else 0
            
            # Add external data (mock)
            add_external_data = options.get('add_external_data', False)
            if add_external_data:
                enriched_data['_external_data'] = {
                    'geo_location': 'Unknown',
                    'timezone': 'UTC',
                    'currency': 'USD'
                }
            
            return {
                'enriched_data': enriched_data,
                'enrichment_summary': {
                    'original_size': len(str(data)),
                    'enriched_size': len(str(enriched_data)),
                    'metadata_added': add_metadata,
                    'computed_fields_added': len(computed_fields),
                    'external_data_added': add_external_data
                }
            }
            
        except Exception as e:
            logger.error(f"Data enrichment failed: {e}")
            raise
    
    async def get_available_scripts(self) -> List[str]:
        """
        Get list of available processing scripts.
        """
        return list(self.available_scripts.keys())
    
    async def get_script_info(self, script_name: str) -> Dict[str, Any]:
        """
        Get information about a specific script.
        """
        if script_name not in self.available_scripts:
            raise ValueError(f"Script '{script_name}' not found")
        
        # Return script information
        script_info = {
            'data_cleaner': {
                'description': 'Clean data by removing null values and empty strings',
                'options': ['remove_nulls', 'remove_empty_strings']
            },
            'data_validator': {
                'description': 'Validate data structure and content',
                'options': ['required_fields', 'field_types', 'value_ranges', 'deprecated_fields']
            },
            'data_transformer': {
                'description': 'Transform data structure and values',
                'options': ['field_mapping', 'value_transformations', 'computed_fields']
            },
            'data_aggregator': {
                'description': 'Aggregate data by groups or globally',
                'options': ['group_by', 'aggregations']
            },
            'data_filter': {
                'description': 'Filter data based on criteria',
                'options': ['filters']
            },
            'data_enricher': {
                'description': 'Enrich data with additional information',
                'options': ['add_metadata', 'computed_fields', 'add_external_data']
            }
        }
        
        return script_info.get(script_name, {'description': 'Unknown script', 'options': []})