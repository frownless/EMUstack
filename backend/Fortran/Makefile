# Makefile for EMUstack. Requires some adjustment to reflect your installation.

# COMPILER_VENDOR = gnu95
COMPILER_VENDOR = intelem

SUBROUTINES_FOR_PYTHON = py_calc_modes.f

LIB_LOCATION = Lib
UMFPACK_NAME = umf4_f77zwrapper64.o





#------------------------------------------------------------------
# IF using Ubuntu SuiteSparse and full ARPACK install
EMUstack.so: EMUstack.pyf Lib/umf4_f77zwrapper64.o *.f
	f2py -c EMUstack.pyf *.f $(LIB_LOCATION)/$(UMFPACK_NAME) -larpack \
	--link-lapack_opt --link-umfpack --link-blas_opt --fcompiler=$(COMPILER_VENDOR)
# With installed libsuitesparse v. < 4.0.0
Lib/umf4_f77zwrapper64.o: Lib/umf4_f77zwrapper_SS_3.7.1.c
	gcc -O5 -DZLONG -I/usr/include/suitesparse -c Lib/umf4_f77zwrapper_SS_3.7.1.c \
		-fPIC -o Lib/umf4_f77zwrapper64.o
# With installed libsuitesparse v. >= 4.0.0
# Lib/umf4_f77zwrapper64.o: Lib/umf4_f77zwrapper_SS_4.2.0.c
# 	gcc -DZLONG -I/usr/include/suitesparse -c Lib/umf4_f77zwrapper_SS_4.2.0.c \
# 		-fPIC -o umf4_f77zwrapper64.o
EMUstack.pyf: $(SUBROUTINES_FOR_PYTHON)
	f2py -m EMUstack -h EMUstack.pyf $(SUBROUTINES_FOR_PYTHON) --overwrite-signature
purge:
	-rm EMUstack.pyf
	-rm EMUstack.so
	-rm Lib/umf4_f77zwrapper64.o
clean:
	-rm EMUstack.so
#------------------------------------------------------------------



# #------------------------------------------------------------------
# # ELSE IF using self built SuiteSparse and Fortran_EMUstack/zarpack.f
# EMUstack.so: EMUstack.pyf *.f
# 	f2py -c EMUstack.pyf *.f --fcompiler=$(COMPILER_VENDOR) \
#         --link-lapack_opt --link-blas_opt \
#         -lrt $(LIB_LOCATION)/$(UMFPACK_NAME) \
#         -L$(LIB_LOCATION) -lumfpack -lamd -lcholmod \
#         -lcolamd -lcamd -lmetis -lccolamd -lamd -lsuitesparseconfig 
# # OR if using both self built SuiteSparse and self built ARPACK (where you cannot ??? add to path?)
# # ARPACK_LIB_LOCATION = /suphys/bjorn/Usyd_Running/f2py-EMUstack/EMUstack/Fortran_EMUstack/ARPACK
# # EMUstack.so: EMUstack.pyf *.f
# # 	f2py -c EMUstack.pyf *.f --fcompiler=$(COMPILER_VENDOR) \
# #         --link-lapack_opt --link-blas_opt \
# #         $(LDADD) -L$(ARPACK_LIB_LOCATION) -larpack \
# #         $(SS_LIB_LOCATION)/$(UMFPACK_NAME) \
# #         -L$(SS_LIB_LOCATION) -lumfpack -lamd -lcholmod \
# #         -lcolamd -lcamd -lmetis -lccolamd -lamd -lsuitesparseconfig 
# EMUstack.pyf: $(SUBROUTINES_FOR_PYTHON)
# 	f2py -m EMUstack -h EMUstack.pyf $(SUBROUTINES_FOR_PYTHON) --overwrite-signature
# purge:
# 	-rm EMUstack.pyf
# 	-rm EMUstack.so
# clean:
# 	-rm EMUstack.so
# #------------------------------------------------------------------