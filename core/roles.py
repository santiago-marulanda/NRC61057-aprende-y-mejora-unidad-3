ROLE_COMPRADOR = "comprador"
ROLE_VENDEDOR = "vendedor"

GROUP_COMPRADORES = "Compradores"
GROUP_VENDEDORES = "Vendedores"


def get_user_roles(user):
    if not getattr(user, "is_authenticated", False):
        return []

    group_names = set(user.groups.values_list("name", flat=True))
    roles = []
    if GROUP_COMPRADORES in group_names:
        roles.append(ROLE_COMPRADOR)
    if GROUP_VENDEDORES in group_names:
        roles.append(ROLE_VENDEDOR)
    # Los superusuarios deben poder operar como rol vendedor aunque no pertenezcan a grupos.
    if getattr(user, "is_superuser", False) and ROLE_VENDEDOR not in roles:
        roles.append(ROLE_VENDEDOR)
    return roles


def get_default_role(user):
    roles = get_user_roles(user)
    if ROLE_VENDEDOR in roles:
        return ROLE_VENDEDOR
    if ROLE_COMPRADOR in roles:
        return ROLE_COMPRADOR
    return None


def get_active_role(request):
    roles = get_user_roles(request.user)
    if not roles:
        request.session.pop("rol_activo", None)
        return None

    current = request.session.get("rol_activo")
    if current in roles:
        return current

    default = get_default_role(request.user)
    if default:
        request.session["rol_activo"] = default
    return default
