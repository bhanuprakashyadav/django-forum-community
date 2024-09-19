from django.contrib.auth.models import Group, Permission

def create_groups_permission():
    # Create groups
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    moderator_group, _ = Group.objects.get_or_create(name='Moderator')
    user_group, _ = Group.objects.get_or_create(name='User')

    # Assign permissions to Admin group
    admin_permissions = Permission.objects.all()  # Admin gets all permissions
    for perm in admin_permissions:
        admin_group.permissions.add(perm)

    # Assign permissions to Moderator group
    moderator_permissions = [
        Permission.objects.get(codename='can_delete_any_reply'),
        Permission.objects.get(codename='can_delete_any_post'),
    ]

    for perm in moderator_permissions:
        moderator_group.permissions.add(perm)

    print("Groups and permissions created successfully!")
