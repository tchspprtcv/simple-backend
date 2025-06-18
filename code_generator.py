import argparse
import os
import json
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Case conversion functions
def to_camel_case(name):
    name = re.sub(r'[\s_-]+', ' ', name)
    parts = name.split(' ')
    return "".join(p[0].upper() + p[1:] if p else "" for p in parts)

def to_pascal_case(name):
    name = re.sub(r'[\s_-]+', ' ', name)
    parts = name.split(' ')
    return "".join(p[0].upper() + p[1:] if p else "" for p in parts)

def to_lower_camel_case(name):
    pascal = to_pascal_case(name)
    return pascal[0].lower() + pascal[1:] if pascal else ''

# Type mapping function
def map_type(igrp_type, attr_config=None):
    if attr_config:
        object_type = attr_config.get('objectType')
        if object_type == 'enum':
            return to_pascal_case(igrp_type)

        original_type_from_config = attr_config.get('type', '').lower()
        if original_type_from_config == 'relation':
            relation_info = attr_config.get('relation')
            if relation_info:
                related_entity_name = to_pascal_case(relation_info.get('entity'))
                if not related_entity_name.endswith("Entity"):
                    related_entity_name += "Entity"

                relation_kind = relation_info.get('type')
                if relation_kind == 'OneToMany':
                    return f"java.util.List<{related_entity_name}>"
                elif relation_kind in ['ManyToOne', 'OneToOne']:
                    return related_entity_name
            print(f"Warning: Relation type for attribute '{attr_config.get('name')}' (type: '{igrp_type}') could not be fully determined. Defaulting to 'Object'.")
            return "Object"

    igrp_type_lower = igrp_type.lower()
    mapping = {
        "string": "String", "text": "String",
        "integer": "Integer", "number": "Integer", "long": "Long",
        "date": "java.time.LocalDate", "datetime": "java.time.LocalDateTime",
        "boolean": "Boolean",
        "double": "Double", "float": "Float",
        "decimal": "java.math.BigDecimal", "bigdecimal": "java.math.BigDecimal",
        "binary": "byte[]"
    }
    if igrp_type_lower in mapping:
        return mapping[igrp_type_lower]

    print(f"Warning: Type '{igrp_type}' is unknown after all checks (attr_config: {attr_config}). Defaulting to 'Object'.")
    return "Object"

# Generation functions (Enum, Entity, DTO, Repo, Mapper, Commands, Queries, Controller)
def generate_enum_files(template_env, base_output_dir, module_name_original, igrp_studio_path):
    print(f"Generating Enums for module: {module_name_original}")
    module_name_lower = module_name_original.lower()
    package_name = f"cv.igrp.simple.{module_name_lower}"

    enum_json_path = igrp_studio_path / module_name_original / "enums"
    if not enum_json_path.is_dir():
        print(f"Info: Enums directory not found for module {module_name_original} at {enum_json_path}. Skipping enum generation.")
        return

    output_dir = Path(base_output_dir) / module_name_original / "domain" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    for enum_file in enum_json_path.glob("*.json"):
        try:
            with open(enum_file, 'r') as f:
                enum_config = json.load(f)
            enum_name = to_pascal_case(enum_config['name'])
            raw_values = enum_config.get('values', [])
            processed_values = []
            details_structure = enum_config.get('value_details_structure', {})

            if raw_values:
                is_simple_list = isinstance(raw_values[0], str)
                if not is_simple_list and isinstance(raw_values[0], dict) and not details_structure:
                    if raw_values[0].get("details"):
                        for key in raw_values[0]["details"].keys():
                            details_structure[key] = "String"

                for val_item in raw_values:
                    if isinstance(val_item, dict):
                        processed_values.append({
                            "name": val_item["name"],
                            "details": val_item.get("details"),
                            "details_structure": details_structure
                        })
                    else:
                        processed_values.append({"name": str(val_item), "details": None, "details_structure": {}})

            context = {"package_name": package_name, "enum_name": enum_name, "values": processed_values}
            template = template_env.get_template("Enum.java.j2")
            rendered_code = template.render(context)
            with open(output_dir / f"{enum_name}.java", "w") as f:
                f.write(rendered_code)
            print(f"Generated Enum: {output_dir / f'{enum_name}.java'}")
        except Exception as e:
            print(f"Error processing enum {enum_file.name}: {e}")

def generate_entity_files(entity_config, base_output_dir, template_env, module_name_original, entity_base_name):
    table_name = entity_config.get('tableName', f"tbl_{entity_base_name.lower()}")
    attributes = []
    for attr_config in entity_config.get('attributes', []):
        attr_name_camel = to_lower_camel_case(attr_config['name'])
        attr_type = map_type(attr_config['type'], attr_config)
        is_enum = attr_config.get('objectType') == 'enum'
        is_relation = attr_config.get('type') == 'relation'
        is_one_to_many, is_many_to_one, is_one_to_one = False, False, False
        mapped_by, join_column_name = None, attr_config['name']

        if is_relation:
            relation_info = attr_config.get('relation', {})
            relation_kind = relation_info.get('type')
            if relation_kind == 'OneToMany':
                is_one_to_many = True
                mapped_by = relation_info.get('mappedBy', to_lower_camel_case(entity_base_name))
            elif relation_kind == 'ManyToOne': is_many_to_one = True
            elif relation_kind == 'OneToOne': is_one_to_one = True

        attributes.append({
            "name": attr_name_camel, "type": attr_type,
            "is_id": attr_config.get('primaryKey', False),
            "generation_type": attr_config.get('generationType'),
            "column_name": attr_config['name'], "nullable": attr_config.get('nullable', True),
            "length": attr_config.get('length'),
            "is_not_blank_from_json": attr_config.get('nullable') is False and attr_config.get('type', '').lower() in ['string', 'text'],
            "is_enum": is_enum, "is_relation": is_relation,
            "is_one_to_many": is_one_to_many, "is_many_to_one": is_many_to_one, "is_one_to_one": is_one_to_one,
            "mapped_by": mapped_by, "join_column_name": join_column_name
        })
    package_name = f"cv.igrp.simple.{module_name_original.lower()}"
    context = {
        "package_name": package_name, "module_name": module_name_original,
        "entity_name": entity_base_name, "table_name": table_name, "attributes": attributes
    }
    output_dir = Path(base_output_dir) / module_name_original / "domain" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file_path = output_dir / f"{entity_base_name}Entity.java"
    try:
        template = template_env.get_template("Entity.java.j2")
        with open(output_file_path, "w") as f:
            f.write(template.render(context))
        print(f"Generated entity: {output_file_path}")
    except Exception as e:
        print(f"Error generating entity {entity_base_name}Entity.java: {e}")

def get_id_type(entity_config):
    for attr_cfg in entity_config.get('attributes', []):
        if attr_cfg.get('primaryKey', False):
            return map_type(attr_cfg['type'], attr_cfg)
    return "Integer"

def generate_dto_files(entity_config, base_output_dir, template_env, module_name_original, entity_base_name):
    package_name = f"cv.igrp.simple.{module_name_original.lower()}"
    attributes, id_attribute = [], None
    for attr_cfg in entity_config.get('attributes', []):
        attr_data = {
            "name": to_lower_camel_case(attr_cfg['name']),
            "type": map_type(attr_cfg['type'], attr_cfg),
            "is_id": attr_cfg.get('primaryKey', False)
        }
        attributes.append(attr_data)
        if attr_data["is_id"]: id_attribute = attr_data
    id_type = id_attribute["type"] if id_attribute else "Integer"

    context = {
        "package_name": package_name, "module_name": module_name_original,
        "entity_name": entity_base_name, "attributes": attributes, "id_type": id_type
    }
    output_dir = Path(base_output_dir) / module_name_original / "application" / "dto"
    output_dir.mkdir(parents=True, exist_ok=True)
    for dto_type_name in ["Create", "Update", "Response"]:
        template_name = f"{dto_type_name}DTO.java.j2"
        output_file_name = f"{entity_base_name}ResponseDTO.java" if dto_type_name == "Response" else f"{dto_type_name}{entity_base_name}DTO.java"
        try:
            template = template_env.get_template(template_name)
            with open(output_dir / output_file_name, "w") as f:
                f.write(template.render(context))
            print(f"Generated DTO: {output_dir / output_file_name}")
        except Exception as e:
            print(f"Error generating DTO {output_file_name}: {e}")

def generate_repository_file(entity_config, base_output_dir, template_env, module_name_original, entity_base_name):
    package_name = f"cv.igrp.simple.{module_name_original.lower()}"
    id_type = get_id_type(entity_config)
    context = {"package_name": package_name, "entity_name": entity_base_name, "id_type": id_type}
    output_dir = Path(base_output_dir) / module_name_original / "domain" / "repository"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file_path = output_dir / f"I{entity_base_name}Repository.java"
    try:
        template = template_env.get_template("Repository.java.j2")
        with open(output_file_path, "w") as f:
            f.write(template.render(context))
        print(f"Generated Repository: {output_file_path}")
    except Exception as e:
        print(f"Error generating repository I{entity_base_name}Repository.java: {e}")

def generate_mapper_file(template_env, base_output_dir, module_name_original, entity_base_name):
    package_name = f"cv.igrp.simple.{module_name_original.lower()}"
    context = {"package_name": package_name, "entity_base_name": entity_base_name}
    output_dir = Path(base_output_dir) / module_name_original / "application" / "mapper"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file_path = output_dir / f"{entity_base_name}Mapper.java"
    try:
        template = template_env.get_template("Mapper.java.j2")
        with open(output_file_path, "w") as f:
            f.write(template.render(context))
        print(f"Generated Mapper: {output_file_path}")
    except Exception as e:
        print(f"Error generating mapper {entity_base_name}Mapper.java: {e}")

def generate_command_files(template_env, base_output_dir, module_name_original, entity_base_name, id_type, entity_var_name):
    package_name = f"cv.igrp.simple.{module_name_original.lower()}"
    context = {"package_name": package_name, "entity_base_name": entity_base_name, "id_type": id_type, "entity_var_name": entity_var_name}
    for action in ["Create", "Update", "Delete"]:
        cmd_name = f"{action}{entity_base_name}Command"
        hdl_name = f"{action}{entity_base_name}CommandHandler"
        tpl_cmd, tpl_hdl = f"Command/{action}Command.java.j2", f"Command/{action}CommandHandler.java.j2"
        out_dir = Path(base_output_dir) / module_name_original / "application" / "commands" / f"{action.lower()}{entity_base_name}"
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            template = template_env.get_template(tpl_cmd)
            with open(out_dir / f"{cmd_name}.java", "w") as f: f.write(template.render(context))
            print(f"Generated Command: {out_dir / f'{cmd_name}.java'}")
        except Exception as e: print(f"Error generating command {cmd_name}.java: {e}")
        try:
            template = template_env.get_template(tpl_hdl)
            with open(out_dir / f"{hdl_name}.java", "w") as f: f.write(template.render(context))
            print(f"Generated Command Handler: {out_dir / f'{hdl_name}.java'}")
        except Exception as e: print(f"Error generating command handler {hdl_name}.java: {e}")

def generate_query_files(template_env, base_output_dir, module_name_original, entity_base_name, id_type, entity_var_name, list_action_request_params=None):
    package_name = f"cv.igrp.simple.{module_name_original.lower()}"
    final_list_params = list_action_request_params if list_action_request_params is not None else []
    queries = [
        {"action": "List", "prefix": "ListaDe", "suffix": "Query", "params": final_list_params},
        {"action": "GetById", "prefix": "Get", "suffix": "ByIdQuery", "params": []}
    ]
    for q_info in queries:
        action, prefix, suffix, params = q_info["action"], q_info["prefix"], q_info["suffix"], q_info["params"]
        query_name = f"{prefix}{entity_base_name}{suffix}"
        handler_name = f"{prefix}{entity_base_name}QueryHandler" if action == "List" else f"{query_name}Handler"
        tpl_query, tpl_hdl = f"Query/{action}Query.java.j2", f"Query/{action}QueryHandler.java.j2"
        q_subdir = f"{action.lower()}{entity_base_name}"
        if action == "GetById": q_subdir = f"get{entity_base_name}ById"
        out_dir = Path(base_output_dir) / module_name_original / "application" / "queries" / q_subdir
        out_dir.mkdir(parents=True, exist_ok=True)

        ctx = {"package_name": package_name, "entity_base_name": entity_base_name, "id_type": id_type, "entity_var_name": entity_var_name, "request_params": params}
        try:
            template = template_env.get_template(tpl_query)
            with open(out_dir / f"{query_name}.java", "w") as f: f.write(template.render(ctx))
            print(f"Generated Query: {out_dir / f'{query_name}.java'}")
        except Exception as e: print(f"Error generating query {query_name}.java: {e}")
        try:
            hdl_ctx = {k: v for k, v in ctx.items() if k != "request_params"}
            template = template_env.get_template(tpl_hdl)
            with open(out_dir / f"{handler_name}.java", "w") as f: f.write(template.render(hdl_ctx))
            print(f"Generated Query Handler: {out_dir / f'{handler_name}.java'}")
        except Exception as e: print(f"Error generating query handler {handler_name}.java: {e}")

def get_entity_base_name(entity_config_name: str) -> str:
    name_pascal = to_pascal_case(entity_config_name)
    return name_pascal[:-6] if name_pascal.endswith("Entity") else name_pascal

def derive_action_type(action_name_from_json, entity_base_name): # entity_base_name passed for context, not strictly used in current generic logic
    action_name_lower = action_name_from_json.lower()
    if "listade" in action_name_lower or "getall" in action_name_lower or action_name_lower.startswith("lista"): return "listaDe"
    if "obter" in action_name_lower or "getbyid" in action_name_lower: return "obter"
    if "criar" in action_name_lower or "create" in action_name_lower or action_name_lower.startswith("post"): return "criar"
    if "atualizar" in action_name_lower or "update" in action_name_lower or action_name_lower.startswith("put"): return "atualizar"
    if "inativar" in action_name_lower: return "inativar"
    if "delete" in action_name_lower or "remove" in action_name_lower: return "delete"
    print(f"Warning: Could not derive specific action type for '{action_name_from_json}'.")
    return action_name_from_json

def generate_controller_file(template_env, base_output_dir, module_name_original, entity_base_name, id_type, controller_config): # Now takes controller_config directly
    print(f"Generating Controller for {entity_base_name} using {controller_config['name']}")
    package_name = f"cv.igrp.simple.{module_name_original.lower()}"
    controller_name_json = to_pascal_case(controller_config['name'])
    class_name = controller_name_json if controller_name_json.endswith("Controller") else controller_name_json + "Controller"

    parsed_actions = []
    for action_conf in controller_config.get('actions', []):
        action_name_json = action_conf['actionName']
        # Pass entity_base_name to derive_action_type for better context if needed, though current derive_action_type is generic
        derived_type = derive_action_type(action_name_json, entity_base_name)
        req_params = []
        if derived_type == "listaDe" and 'requestParams' in action_conf:
            for rp_conf in action_conf['requestParams']:
                req_params.append({
                    "name": rp_conf['name'], "name_camel_case": to_lower_camel_case(rp_conf['name']),
                    "type": map_type(rp_conf['type'], rp_conf), # Pass rp_conf for enum/obj type checking
                    "is_required": rp_conf.get('isRequired', False)
                })
        parsed_actions.append({
            "action_name": action_name_json, "derived_action_type": derived_type,
            "method_name": to_lower_camel_case(action_name_json),
            "http_method": action_conf.get('httpMethod', 'GET'), "path": action_conf.get('path', ''),
            "request_params": req_params
        })

    context = {
        "package_name": package_name, "module_name": module_name_original,
        "entity_base_name": entity_base_name, "id_type": id_type,
        "controller_name": class_name, "base_path": controller_config.get('basePath', f"/api/v1/{entity_base_name.lower()}s"),
        "controller_tag": controller_config.get('description', entity_base_name), "actions": parsed_actions
    }
    output_dir = Path(base_output_dir) / module_name_original / "infrastructure" / "controller"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file_path = output_dir / f"{class_name}.java"
    try:
        template = template_env.get_template("Controller.java.j2")
        with open(output_file_path, "w") as f: f.write(template.render(context))
        print(f"Generated Controller: {output_file_path}")
    except Exception as e: print(f"Error generating controller {class_name}.java: {e}")

def generate_module(module_name, base_output_dir="generated_output", template_dir="templates"):
    print(f"Generating module: {module_name}")
    template_loader = FileSystemLoader(searchpath=template_dir)
    template_env = Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True)
    igrp_studio_path = Path(".igrpstudio")

    # Phase 1: Generate Enums
    generate_enum_files(template_env, base_output_dir, module_name, igrp_studio_path)

    # Phase 2: Load all entity and controller configurations
    entity_configs = {}
    module_models_path = igrp_studio_path / module_name / "models"
    if module_models_path.is_dir():
        for f_path in module_models_path.glob("*.json"):
            try:
                with open(f_path, 'r') as f: cfg = json.load(f)
                entity_configs[get_entity_base_name(cfg['name'])] = cfg
            except Exception as e: print(f"Error loading entity model {f_path.name}: {e}")
    else: print(f"Warning: Models directory not found: {module_models_path}")

    controller_data_map = {} # Stores {"config": cfg, "list_action_request_params": []}
    module_controllers_path = igrp_studio_path / module_name / "controllers"
    if module_controllers_path.is_dir():
        for f_path in module_controllers_path.glob("*Controller.json"):
            try:
                with open(f_path, 'r') as f: cfg = json.load(f)
                controller_name_pascal = to_pascal_case(cfg['name'])
                primary_entity = controller_name_pascal.replace("Controller", "")

                parsed_list_params = []
                for action_conf in cfg.get('actions', []):
                    # Use primary_entity for context in derive_action_type
                    if derive_action_type(action_conf['actionName'], primary_entity) == "listaDe" and 'requestParams' in action_conf:
                        for rp_conf in action_conf['requestParams']:
                            parsed_list_params.append({
                                "name": rp_conf['name'], "name_camel_case": to_lower_camel_case(rp_conf['name']),
                                "type": map_type(rp_conf['type'], rp_conf), # Pass rp_conf here
                                "is_required": rp_conf.get('isRequired', False)
                            })
                        break # Found list action's params for this controller
                controller_data_map[primary_entity] = {
                    "config": cfg,
                    "list_action_request_params": parsed_list_params
                }
            except Exception as e: print(f"Error loading controller {f_path.name}: {e}")
    else: print(f"Warning: Controllers directory not found: {module_controllers_path}")

    # Phase 3: Generate entity-specific files
    if not entity_configs: print(f"No entities to process for module {module_name}.")
    for entity_base_name, entity_config in entity_configs.items():
        print(f"Generating files for entity: {entity_base_name}")
        try:
            id_type = get_id_type(entity_config)
            entity_var_name = to_lower_camel_case(entity_base_name)

            current_entity_controller_data = controller_data_map.get(entity_base_name, {})
            list_action_params_for_entity = current_entity_controller_data.get("list_action_request_params", [])

            generate_entity_files(entity_config, base_output_dir, template_env, module_name, entity_base_name)
            generate_dto_files(entity_config, base_output_dir, template_env, module_name, entity_base_name)
            generate_repository_file(entity_config, base_output_dir, template_env, module_name, entity_base_name)
            generate_mapper_file(template_env, base_output_dir, module_name, entity_base_name)
            generate_command_files(template_env, base_output_dir, module_name, entity_base_name, id_type, entity_var_name)
            generate_query_files(template_env, base_output_dir, module_name, entity_base_name, id_type, entity_var_name, list_action_params_for_entity)
        except Exception as e: print(f"Error generating files for entity {entity_base_name}: {e}")

    # Phase 4: Generate Controllers
    if not controller_data_map: print(f"No controllers to generate for module {module_name}.")
    for primary_entity_base_name, data in controller_data_map.items():
        controller_config = data["config"]
        if primary_entity_base_name in entity_configs:
            entity_id_type = get_id_type(entity_configs[primary_entity_base_name])
            # Pass controller_config directly to generate_controller_file
            generate_controller_file(template_env, base_output_dir, module_name, primary_entity_base_name, entity_id_type, controller_config)
        else:
            print(f"Warning: Entity info for '{primary_entity_base_name}' not found. Skipping controller '{controller_config['name']}'.")

def main():
    parser = argparse.ArgumentParser(description="Generate Java code from IGRP Studio JSON configurations.")
    parser.add_argument("module_name", help="The name of the module to generate code for (e.g., 'Utente').")
    parser.add_argument("--output_dir", default="generated_output", help="The base directory for generated code.")
    parser.add_argument("--template_dir", default="templates", help="The directory containing Jinja2 templates.")
    args = parser.parse_args()
    generate_module(args.module_name, args.output_dir, args.template_dir)

if __name__ == "__main__":
    main()
