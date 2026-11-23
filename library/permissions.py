from rest_framework.permissions import BasePermission

class IsLibrarian(BasePermission):
    def has_permission(self,request,view):
        return request.user.groups.filter(name="Librarian").exists()

class IsMember(BasePermission):
    def has_permission(self,request,view):
        return request.user.groups.filter(name="Member").exists()

class IsLibrarianOrReadOnly(BasePermission):
    def has_permission(self,request,view):
        if request.method in ('GET','HEAD','OPTIONS'):
            return True
        return request.user.groups.filter(name='Librarian').exists()

class IsMemberOrLibrarian(BasePermission):
    def has_permission(self,request,view):
        return request.user.groups.filter(
            name__in=['Member','Librarian']
        ).exists()
