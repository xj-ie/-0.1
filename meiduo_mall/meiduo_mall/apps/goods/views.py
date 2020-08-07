from django.shortcuts import render

# Create your views here.

class A(object):
    def _open(self, file):
        print(file)
    def open(self,name , file):
        self._open(file)
        return name
    def url(self,name):
        print(2)


class B(A):
    def url(self,name):
        print(1)



b = B()
b.url(1)
