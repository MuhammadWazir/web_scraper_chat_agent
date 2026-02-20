from typing import List, Dict, Optional, Any
import requests
import json


def convert_value(value: Any, schema: Dict[str, Any], field_name: str = "") -> Any:
    """
    Convert a value to match the expected type in the schema.
    Handles Cal.com's strict type requirements.
    """
    # Get the target type from schema
    target_type = schema.get("type")
    
    # Handle legacy "fields" notation (convert to object)
    if "fields" in schema and not target_type:
        target_type = "object"
    
    # Auto-detect type if not specified
    if not target_type:
        if isinstance(value, bool):
            target_type = "boolean"
        elif isinstance(value, (int, float)):
            target_type = "number"
        elif isinstance(value, dict):
            target_type = "object"
        elif isinstance(value, list):
            target_type = "array"
        else:
            target_type = "string"
    
    # Aggressive number detection for common field names
    if field_name:
        fn_lower = field_name.lower()
        # Check for common numeric suffixes
        if any(suffix in fn_lower for suffix in ["id", "count", "minutes", "duration", "limit", "offset", "take", "skip"]):
            # If it's already a number, keep it
            if isinstance(value, (int, float)):
                target_type = "number"
            # If it's a string that looks like a number, convert it
            elif isinstance(value, str) and value.replace(".", "", 1).replace("-", "", 1).isdigit():
                target_type = "number"
    
    # Type conversion logic
    if target_type == "number":
        try:
            if isinstance(value, str):
                # Convert string to int or float
                return int(value) if '.' not in value else float(value)
            elif isinstance(value, (int, float)):
                return value
            else:
                # Try to convert other types
                return float(value)
        except (ValueError, TypeError):
            return value
    
    elif target_type == "object":
        # Handle nested objects with properties or fields
        nested_key = "properties" if "properties" in schema else "fields" if "fields" in schema else None
        
        if isinstance(value, dict):
            if nested_key and nested_key in schema:
                # Recursively convert nested properties
                converted = {}
                for key, val in value.items():
                    if key in schema[nested_key]:
                        converted[key] = convert_value(val, schema[nested_key][key], key)
                    else:
                        # Keep unknown properties as-is
                        converted[key] = val
                return converted
            else:
                # No schema for nested properties, return as-is
                return value
        elif isinstance(value, str):
            # Try to parse JSON string
            try:
                import json
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except:
                pass
        return value
    
    elif target_type == "array":
        # Ensure value is a list
        if not isinstance(value, list):
            value = [value]
        
        # Convert array items if schema is provided
        if "items" in schema and isinstance(schema["items"], dict):
            items_schema = schema["items"]
            return [convert_value(item, items_schema, field_name + "_item") for item in value]
        
        return value
    
    elif target_type == "boolean":
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ("true", "1", "yes")
        return bool(value)
    
    elif target_type == "string":
        # For strings, preserve complex types (don't stringify objects/arrays)
        if isinstance(value, (dict, list)):
            return value
        return str(value)
    
    # Default: return as-is for unknown types
    return value


def execute_endpoint(
    endpoint: Dict[str, Any],
    args: Dict[str, Any],
    auth_token: Optional[str] = None,
    oauth_client_id: Optional[str] = None,
    oauth_client_secret: Optional[str] = None
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
            body[key] = convert_value(args[key], schema)

    # Handle auth - check for oauth_or_apiKey or bearer
    auth_type = endpoint.get("auth", "")
    
    # Get OAuth credentials from endpoint config if available
    oauth_client_id = endpoint.get("oauth_client_id")
    oauth_client_secret = endpoint.get("oauth_client_secret")
    
    if auth_type in ("bearer", "oauth_or_apiKey"):
        # Use provided auth_token if available
        if auth_token:
            headers["Authorization"] = auth_token
        # If no auth_token but we have OAuth credentials in endpoint config, try to get access token
        elif oauth_client_id and oauth_client_secret:
            # Try to get OAuth access token
            try:
                base_url = endpoint.get("base_url", "").rstrip("/")
                oauth_url = f"{base_url}/oauth/token"
                oauth_response = requests.post(
                    oauth_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": oauth_client_id,
                        "client_secret": oauth_client_secret
                    },
                    timeout=10
                )
                if oauth_response.ok:
                    token_data = oauth_response.json()
                    access_token = token_data.get("access_token")
                    if access_token:
                        headers["Authorization"] = f"Bearer {access_token}"
            except Exception:
                pass  # Fall back to no auth

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
        
        # Handle legacy "fields" notation
        if "fields" in schema and "type" not in schema:
            schema["type"] = "object"
        
        # Aggressive number type detection for common field names
        if "type" not in schema or schema.get("type") == "string":
            if any(suffix in name.lower() for suffix in ["id", "count", "minutes", "duration", "limit", "offset", "take", "skip"]):
                # Always treat these as numbers
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