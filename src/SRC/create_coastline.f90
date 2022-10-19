! Script to generate a mask (1 and 0) of the oceanic coastline for usage in the
! PISCES with the runoff dependant river input of nutrients.
! JBL - 03.11.2017

!Pour compiler
!ifort -o "createcoast" $NETCDFFORTRAN_LDFLAGS $NETCDFC_LDFLAGS $NETCDFFORTRAN_FFLAGS $NETCDFC_CFLAGS create_coastline.f90


PROGRAM COAST
 
use netcdf

implicit none

integer, parameter :: imax=182, jmax=149
integer, parameter :: kmax=31, lmax=1
integer :: i, j, im1, ip1, jm1, jp1
integer :: k
integer :: status, ncid1, ncid2, ncid3
integer :: xdimid, ydimid
integer :: navlonvarid, navlatvarid, coastvarid
integer :: varid1, varid2, varid3
real,dimension(imax,jmax) :: lon, lat, coastmsk 
!real,dimension(imax,jmax) :: inbathy 
real,dimension(imax,jmax,kmax,lmax) :: inbathy 

! Read netcdf bathy.nc
status = nf90_open("bathyPALEORCA2.70Ma_Corr.nc",nf90_nowrite,ncid1)
if(status /= nf90_NoErr) print *,"Error occured (1.1)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_inq_varid(ncid1,"Bathymetry",varid1)
!status = nf90_inq_varid(ncid1,"tmask",varid1)
if(status /= nf90_NoErr) print *,"Error occured (1.2)"
if(status /= nf90_NoErr) call handle_err(status)

!status = nf90_get_var(ncid1,varid1,inbathy(:,:))
status = nf90_get_var(ncid1,varid1,inbathy(:,:,:,:))
if(status /= nf90_NoErr) print *,"Error occured (1.3)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_inq_varid(ncid1,"nav_lon",varid2)
if(status /= nf90_NoErr) print *,"Error occured (1.4)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_get_var(ncid1,varid2,lon(:,:))
if(status /= nf90_NoErr) print *,"Error occured (1.5)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_inq_varid(ncid1,"nav_lat",varid3)
if(status /= nf90_NoErr) print *,"Error occured (1.6)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_get_var(ncid1,varid3,lat(:,:))
if(status /= nf90_NoErr) print *,"Error occured (1.7)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_close(ncid1)

write(*,*) 'size tmask :', size(inbathy,3)

!stop 5

! Create right bathy netcdf
status = nf90_create("70Ma-4X.mask.from.tmask.nc",nf90_noclobber,ncid3)
if(status /= nf90_NoErr) print *,"Error occured (3.1)"
if(status /= nf90_NoErr) call handle_err(status)


!Define dimensions
status = nf90_def_dim(ncid3,"y",149,ydimid)
if(status /= nf90_NoErr) print *,"Error occured (3.2)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_def_dim(ncid3,"x",182,xdimid)
if(status /= nf90_NoErr) print *,"Error occured (3.3)"
if(status /= nf90_NoErr) call handle_err(status)


! Define variables
status = nf90_def_var(ncid3,"nav_lon",nf90_double,& 
                      (/ xdimid, ydimid /),navlonvarid)
if(status /= nf90_NoErr) print *,"Error occured (3.4)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_def_var(ncid3,"nav_lat",nf90_double,& 
                      (/ xdimid, ydimid /),navlatvarid)
if(status /= nf90_NoErr) print *,"Error occured (3.5)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_def_var(ncid3,"cmask",nf90_double,& 
                      (/ xdimid, ydimid /),coastvarid)
if(status /= nf90_NoErr) print *,"Error occured (3.6)"
if(status /= nf90_NoErr) call handle_err(status)


! Set attributes
status = nf90_put_att(ncid3,navlonvarid,"standard_name","longitude")
status = nf90_put_att(ncid3,navlonvarid,"long_name","Longitude")
status = nf90_put_att(ncid3,navlonvarid,"units","degrees_east")
status = nf90_put_att(ncid3,navlonvarid,"_CoordinateAxisType","Lon")

status = nf90_put_att(ncid3,navlatvarid,"standard_name","latitude")
status = nf90_put_att(ncid3,navlatvarid,"long_name","Latitude")
status = nf90_put_att(ncid3,navlatvarid,"units","degrees_north")
status = nf90_put_att(ncid3,navlatvarid,"_CoordinateAxisType","Lat")

status = nf90_put_att(ncid3,coastvarid,"standard_name","coastal points")
status = nf90_put_att(ncid3,coastvarid,"long_name","Coastal points")
status = nf90_put_att(ncid3,coastvarid,"coordinates","nav_lon nav_lat")
status = nf90_put_att(ncid3,coastvarid,"units","-")

status = nf90_close(ncid3)

! Calculations
coastmsk = 0.
where (inbathy .gt. 1) inbathy = 1.
where (inbathy .ne. 1) inbathy = 0.

! Added to comply with the expected result (variable atmmask of the a2o.rivflu.diag.nc file created by MOZAIC scripts).
!inbathy(:,1) = 0.

do j = 2,jmax-1
   jm1 = j-1; jp1 = j+1
   do i = 1, imax

      im1 = i-1; ip1 = i+1

      if (im1 .eq. 0) im1 = imax
      if (ip1 .gt. imax) ip1 = 1
  
      do k = jm1,jp1,1
         !if ((inbathy(i,j) .eq. 1.) .and. ((inbathy(im1,k) .eq. 0.) .or. (inbathy(ip1,k) .eq. 0.) .or. (inbathy(i,jm1) .eq. 0.) .or. (inbathy(i,jp1) .eq. 0.))) then
         if ((inbathy(i,j,1,1) .eq. 1.) .and. ((inbathy(im1,k,1,1) .eq. 0.) .or. (inbathy(ip1,k,1,1) .eq. 0.) .or. (inbathy(i,jm1,1,1) .eq. 0.) .or. (inbathy(i,jp1,1,1) .eq. 0.))) then
         
            coastmsk(i,j) = 1.
         
         endif
      enddo

   enddo

enddo

do i = 1,imax
 
   im1 = i-1; ip1 = i+1
   if (im1 .eq. 0) im1 = imax
   if (ip1 .gt. imax) ip1 = 1

      do k = jmax-1,jmax
         !if ((inbathy(i,jmax) .eq. 1.) .and. ((inbathy(im1,k) .eq. 0.) .or. (inbathy(ip1,k) .eq. 0.) .or. (inbathy(i,jmax-1) .eq. 0.))) then
         if ((inbathy(i,jmax,1,1) .eq. 1.) .and. ((inbathy(im1,k,1,1) .eq. 0.) .or. (inbathy(ip1,k,1,1) .eq. 0.) .or. (inbathy(i,jmax-1,1,1) .eq. 0.))) then
   
            coastmsk(i,jmax) = 1.

         endif
      enddo

      do k = 1,2
         !if ((inbathy(i,1) .eq. 1.) .and. ((inbathy(im1,k) .eq. 0.) .or. (inbathy(ip1,k) .eq. 0.) .or. (inbathy(i,2) .eq. 0.))) then
         if ((inbathy(i,1,1,1) .eq. 1.) .and. ((inbathy(im1,k,1,1) .eq. 0.) .or. (inbathy(ip1,k,1,1) .eq. 0.) .or. (inbathy(i,2,1,1) .eq. 0.))) then
   
            coastmsk(i,1) = 1.

         endif
      enddo
   
enddo


! Checks
write(*,*) "Nb of ocean points =", count(inbathy .gt. 0.)
write(*,*) "Nb of coastal points =", count(coastmsk .gt. 0.)

! Save new netcdf
status = nf90_open("70Ma-4X.mask.from.tmask.nc",nf90_write,ncid3)
if(status /= nf90_NoErr) print *,"Error occured (4.1)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_inq_varid(ncid3,"nav_lon",navlonvarid)
if(status /= nf90_NoErr) print *,"Error occured (4.2)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_put_var(ncid3,navlonvarid,lon(:,:))
if(status /= nf90_NoErr) print *,"Error occured (4.3)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_inq_varid(ncid3,"nav_lat",navlatvarid)
if(status /= nf90_NoErr) print *,"Error occured (4.4)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_put_var(ncid3,navlatvarid,lat(:,:))
if(status /= nf90_NoErr) print *,"Error occured (4.5)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_inq_varid(ncid3,"cmask",coastvarid)
if(status /= nf90_NoErr) print *,"Error occured (4.6)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_put_var(ncid3,coastvarid,coastmsk(:,:))
if(status /= nf90_NoErr) print *,"Error occured (4.7)"
if(status /= nf90_NoErr) call handle_err(status)

status = nf90_close(ncid3)


END PROGRAM COAST



SUBROUTINE handle_err(status)

use netcdf

integer, intent(in) :: status

if (status /= nf90_noerr) then
   print *,trim(nf90_strerror(status))
   stop "stopped"
end if

END SUBROUTINE handle_err



