from typing import List, Dict, Optional, Any
import requests
import json


def convert_value(value: Any, schema: Dict[str, Any], field_name: str = "") -> Any:
    # Get target type from schema, defaulting to None (preserve original)
    target_type = schema.get("type")
    
    # Auto-detect type if not specified
    if not target_type:
        if isinstance(value, (int, float)):
            target_type = "number"
        elif isinstance(value, bool):
            target_type = "boolean"
        elif isinstance(value, (dict, list)):
            target_type = "object" if isinstance(value, dict) else "array"
        else:
            target_type = "string"

    # Strict number detection for common suffixes
    if field_name:
        fn_lower = field_name.lower()
        if any(suffix in fn_lower for suffix in ["id", "count", "minutes", "duration", "limit", "offset", "take", "skip"]):
            # If it's a digit string, we should try to make it a number
            if isinstance(value, str) and value.replace(".", "", 1).replace("-", "", 1).isdigit():
                target_type = "number"

    if target_type == "number":
        try:
            if isinstance(value, str):
                return int(value) if '.' not in value else float(value)
            return value
        except (ValueError, TypeError):
            return value
            
    elif target_type == "object" or target_type == "any":
        # For objects, if we have a schema with properties/fields, recurse
        nested_key = "properties" if "properties" in schema else "fields" if "fields" in schema else None
        
        if isinstance(value, dict) and nested_key and nested_key in schema:
            converted = {}
            for key, val in value.items():
                if key in schema[nested_key]:
                    converted[key] = convert_value(val, schema[nested_key][key], key)
                else:
                    converted[key] = val
            return converted
        # If no schema or already a dict, return as is (don't force str())
        return value
        
    elif target_type == "array":
        if not isinstance(value, list):
            return [value]
        
        if "items" in schema and isinstance(schema["items"], dict):
            items_schema = schema["items"]
            return [convert_value(item, items_schema, field_name + "_item") for item in value]
        return value
        
    elif target_type == "boolean":
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return bool(value)
        
    # Default: string, but only force str() if it's a primitive
    if isinstance(value, (dict, list)):
        return value
    return str(value)


def execute_endpoint(
    endpoint: Dict[str, Any],
    args: Dict[str, Any],
    auth_token: Optional[str] = None
) -> Dict[str, Any]:
    base_url = endpoint.get("base_url", "").rstrip("/")
    url = base_url + endpoint["url"]
    method = endpoint["method"].upper()
    headers = endpoint.get("headers", {}).copy()
    params: Dict[str, Any] = {}
    body: Dict[str, Any] = {}
    
    if "headers" in endpoint or "body" in endpoint:
        headers_schema = endpoint.get("headers", {})
        body_schema = endpoint.get("body", {})
        query_schema = endpoint.get("query", {})
        path_schema = endpoint.get("path", {})
    else:
        inputs = endpoint.get("inputs", {})
        if "inputs" in inputs and isinstance(inputs["inputs"], dict):
            inputs = inputs["inputs"]
        headers_schema = inputs.get("headers", {})
        body_schema = inputs.get("body", {})
        query_schema = inputs.get("query", {})
        path_schema = inputs.get("path", {})

    for key, schema in headers_schema.items():
        if isinstance(schema, dict) and "value" in schema:
            headers[key] = schema["value"]
        elif key in args:
            headers[key] = args[key]

    for key in path_schema:
        if key in args:
            url = url.replace(f"{{{key}}}", str(args[key]))

    for key, schema in query_schema.items():
        if key in args:
            params[key] = convert_value(args[key], schema)
        elif isinstance(schema, dict) and "default" in schema:
            params[key] = schema["default"]

    for key, schema in body_schema.items():
        if key in args:
            if isinstance(schema, dict) and "fields" in schema and "type" not in schema:
                schema = {**schema, "type": "object"}
            
            converted = convert_value(args[key], schema)
            
            # For GET requests, if the tool accidentally put fields in body_schema, 
            # move them to query params instead of sending a JSON body.
            if method == "GET":
                params[key] = converted
            else:
                body[key] = converted

    if endpoint.get("auth") == "bearer" and auth_token:
        headers["Authorization"] = auth_token

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params or None,
            json=body or None,
            timeout=30
        )
        
        if not response.ok:
            try:
                error_details = response.json()
            except json.JSONDecodeError:
                error_details = response.text
            
            return {
                "error": "API_ERROR",
                "status_code": response.status_code,
                "details": error_details
            }
            
        return response.json() if response.content else {"status": "success"}
    except Exception as e:
        return {"error": f"EXECUTION_ERROR: {str(e)}"}


def build_properties(section: Dict[str, Any]) -> tuple[Dict[str, Any], List[str]]:
    properties = {}
    required = []
    
    for name, schema in section.items():
        if not isinstance(schema, dict):
            continue
        
        if "fields" in schema and "type" not in schema:
            schema["type"] = "object"
        
        if "type" not in schema or schema.get("type") == "string":
            if any(suffix in name.lower() for suffix in ["id", "count", "minutes", "duration", "limit", "offset", "take", "skip"]):
                schema["type"] = "number"
        
        prop = {"type": schema.get("type", "string")}
        
        nested_key = None
        if schema.get("type") == "object":
            if "properties" in schema:
                nested_key = "properties"
            elif "fields" in schema:
                nested_key = "fields"
        
        if nested_key:
            nested_props, nested_req = build_properties(schema[nested_key])
            prop["properties"] = nested_props
            if nested_req:
                prop["required"] = nested_req
        
        if schema.get("type") == "array":
            if "items" in schema:
                items_schema = schema["items"]
                if isinstance(items_schema, dict):
                    if "properties" in items_schema or "fields" in items_schema:
                        nested_key = "properties" if "properties" in items_schema else "fields"
                        items_props, items_req = build_properties(items_schema.get(nested_key, {}))
                        prop["items"] = {
                            "type": items_schema.get("type", "object"),
                            "properties": items_props
                        }
                        if items_req:
                            prop["items"]["required"] = items_req
                    else:
                        prop["items"] = {"type": items_schema.get("type", "string")}
                else:
                    prop["items"] = items_schema
            else:
                prop["items"] = {"type": "string"}
        
        if "description" in schema:
            prop["description"] = schema["description"]
        
        if "enum" in schema:
            prop["enum"] = schema["enum"]
        
        properties[name] = prop
        
        if schema.get("required"):
            required.append(name)
    
    return properties, required


def build_tools_schema(endpoints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tools = []

    for ep in endpoints:
        if not isinstance(ep, dict):
            continue
            
        properties = {}
        required = []

        if "headers" in ep or "body" in ep:
            sections = {
                "headers": ep.get("headers", {}),
                "body": ep.get("body", {}),
                "query": ep.get("query", {}),
                "path": ep.get("path", {})
            }
        else:
            inputs = ep.get("inputs", {})
            if not isinstance(inputs, dict):
                inputs = {}
            
            if "inputs" in inputs and isinstance(inputs["inputs"], dict):
                inputs = inputs["inputs"]
            
            sections = {
                "headers": inputs.get("headers", {}),
                "body": inputs.get("body", {}),
                "query": inputs.get("query", {}),
                "path": inputs.get("path", {})
            }

        for section_name, section in sections.items():
            if not isinstance(section, dict):
                continue
            
            section_props, section_req = build_properties(section)
            properties.update(section_props)
            required.extend(section_req)

        name = ep.get("name")
        description = ep.get("description", "")
        
        if not name:
            continue

        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False
                }
            }
        })

    return tools
