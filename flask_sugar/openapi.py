from typing import Optional, List, Dict, Union, Any


def get_openapi_json(
    openapi_version: str,
    title: str,
    version: str,
    description: Optional[str] = "",
    terms_service: Optional[str] = None,
    contact: Optional[Dict[str, str]] = None,
    license_: Optional[Dict[str, str]] = None,
    servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
    paths: Optional[Dict[str, Union[str, Any]]] = None,
    components: Optional[List[Dict[str, Union[str, Any]]]] = None,
) -> Dict[str, Any]:
    info: Dict[str, Any] = {"title": title, "version": version}
    if description:
        info["description"] = description
    if terms_service:
        info["termsOfService"] = terms_service
    if contact:
        info["contact"] = contact
    if license_:
        info["license"] = license_
    source = {
        "openapi": openapi_version,
        "info": info,
    }
    if servers:
        source["servers"] = servers
    if paths:
        source["paths"] = paths
    if components:
        source["components"] = components
    return source
