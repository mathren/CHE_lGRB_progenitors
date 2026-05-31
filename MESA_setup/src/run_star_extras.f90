! ***********************************************************************
!
!   Copyright (C) 2012  Bill Paxton
!
!   this file is part of mesa.
!
!   mesa is free software; you can redistribute it and/or modify
!   it under the terms of the gnu general library public license as published
!   by the free software foundation; either version 2 of the license, or
!   (at your option) any later version.
!
!   mesa is distributed in the hope that it will be useful,
!   but without any warranty; without even the implied warranty of
!   merchantability or fitness for a particular purpose.  see the
!   gnu library general public license for more details.
!
!   you should have received a copy of the gnu library general public license
!   along with this software; if not, write to the free software
!   foundation, inc., 59 temple place, suite 330, boston, ma 02111-1307 usa
!
! ***********************************************************************

module run_star_extras

  use star_lib
  use star_def
  use const_def
  use math_lib
  use chem_def
  use num_lib
  use binary_def

  implicit none

contains

  ! include 'Fuller_AM/Fuller_AM_transport.inc'

  subroutine extras_controls(id, ierr)
    integer, intent(in) :: id
    integer, intent(out) :: ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return

    s% extras_startup => extras_startup
    s% extras_start_step => extras_start_step
    s% extras_check_model => extras_check_model
    s% extras_finish_step => extras_finish_step
    s% extras_after_evolve => extras_after_evolve
    s% how_many_extra_history_columns => how_many_extra_history_columns
    s% data_for_extra_history_columns => data_for_extra_history_columns
    s% how_many_extra_profile_columns => how_many_extra_profile_columns
    s% data_for_extra_profile_columns => data_for_extra_profile_columns

    s% how_many_extra_history_header_items => how_many_extra_history_header_items
    s% data_for_extra_history_header_items => data_for_extra_history_header_items
    s% how_many_extra_profile_header_items => how_many_extra_profile_header_items
    s% data_for_extra_profile_header_items => data_for_extra_profile_header_items

    ! if use_other_am_mixing = .true.
    ! s% other_am_mixing => TSF_Fuller_lu22 ! requires MESA_CONTRIB
    s% how_many_other_mesh_fcns => how_many_other_mesh_fcns
    s% other_mesh_fcn_data => resolve_gradients

  end subroutine extras_controls

  subroutine how_many_other_mesh_fcns(id, n)
    integer, intent(in) :: id
    integer, intent(out) :: n
    n = 3
  end subroutine how_many_other_mesh_fcns

  subroutine resolve_gradients( &
       id, nfcns, names, gval_is_xa_function, vals1, ierr)
    use const_def
    integer, intent(in) :: id
    integer, intent(in) :: nfcns
    character (len=*) :: names(:)
    logical, intent(out) :: gval_is_xa_function(:) ! (nfcns)
    real(dp), pointer :: vals1(:)
    real(dp), pointer :: vals(:,:)
    integer, intent(out) :: ierr
    integer :: k, j
    real(dp) :: weight, gradT_across_kj, gradmu_across_kj
    real(dp) :: delta_grada_across_kj, delta_gradr_across_kj
    type (star_info), pointer :: s
    gval_is_xa_function(1:nfcns) = .false.
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) then
       call mesa_error(__FILE__,__LINE__,"problem other_mesh_function resolve_gradients")
    end if

    vals(1:s%nz,1:nfcns) => vals1(1:s%nz*nfcns)

    ! initialize to null
    vals(1:s%nz, 1) = 0.0d0

    names(1) = "nabla_T_across_hp"
    names(2) = "nabla_mu_across_hp"
    names(3) = "delta_grada_across_hp"
    ! names(4) = "delta_gradr_across_hp"

    weight = s% x_ctrl(3) ! weight set in inlist1

    ! aim: resolve all these gradients interpolating across hp
    do k = 1, s%nz-1
       j = k+1
       do while (abs(s%r(k)-s%r(j)) <= s% scale_height(k) .and. j<= s%nz-1)
          j = j + 1 ! move one deeper
       end do
       ! now j is the index of the cell below cell k at distance
       ! equal to the local pressure scale heigh at cell k
       gradT_across_kj = (s% xh(s% i_lnT, k) - s%xh(s% i_lnT, j))/(s% lnPeos(k) - s%lnPeos(j))
       gradmu_across_kj = (log(s% mu(k)) - log(s%mu(j)))/(s% lnPeos(k) - s%lnPeos(j))
       delta_grada_across_kj = abs(s% grada(k) - s%grada(j))
       delta_gradr_across_kj = abs(s% gradr(k) - s%gradr(j))
       vals(k, 1) = weight * gradT_across_kj
       vals(k, 2) = weight * gradmu_across_kj
       vals(k, 3) = weight * delta_grada_across_kj
       ! vals(k, 4) = weight * delta_gradr_across_kj
    end do

    ! enforce a floor: gradients are un-resolvable in 1D!
    ! vals(1:s%nz, 1:nfcns) = max(vals(1:s%nz, 1:nfcns), 1d-4)
    ! print *, "pre floor", minval(vals(1:s%nz, 1:nfcns)), maxval(vals(1:s%nz, 1:nfcns))
    ! where (abs(vals(1:s%nz, 1:nfcns)) < 1.0d-4) vals(1:s%nz, 1:nfcns) = sign(1.0d-4, vals(1:s%nz, 1:nfcns))
    ! where (abs(vals(1:s%nz, 1:nfcns)) > 5.0d3) vals(1:s%nz, 1:nfcns) = sign(5.0d3, vals(1:s%nz, 1:nfcns))
    ! print *, "post floor", minval(vals(1:s%nz, 1:nfcns)), maxval(vals(1:s%nz, 1:nfcns))
  end subroutine resolve_gradients

  integer function get_index_no_v(id, ierr) result(k_no_v)
    integer, intent(in) :: id
    integer, intent(out) :: ierr
    real(dp) :: t_sound_cross
    integer :: k, k0
    type (star_info), pointer :: s
    ! initialize at surface
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) then
       call mesa_error(__FILE__,__LINE__,"problem finding index for v expunging")
    end if
    ! initialize indexes at surface
    k_no_v = 1
    k0 = 1

    ! hack to turn this off from inlist
    if (s% x_ctrl(1)<0) return


    ! if O depletion, start at CO core mass
    if ((s%lxtra(2)) .and. (minval(s% entropy(1:s%nz)) < s%x_ctrl(2))) &
         k0 = min(minloc(abs(s%m(1:s%nz)/Msun - s%co_core_mass), dim=1), &
                  minloc(abs(s% entropy(1:s%nz)- s%x_ctrl(2)), dim=1))

    ! ! if past silicon depletion, owerwrite and start from Si core
    ! if (s% lxtra(3) .eqv. .true.) then
    !    k = k0 ! from previous inner boundary (surface or CO core)
    !    do while ((s% xa(s% net_iso(isi28), k) <= s% min_boundary_fraction) .and. &
    !         ((s% xa(s% net_iso(io16), k) >= 0.1d0)) .and. k<s%nz)
    !       k = k + 1 ! one cell deep
    !    end do
    !    ! if not reached center, we are at si core outer boundary
    !    if (k < s% nz) k0 = k ! update
    ! end if

    ! find point in sonic contact with core edge
    t_sound_cross = 0.0d0
    k_no_v=k0 ! start at core edge
    do while ((t_sound_cross < s%x_ctrl(1) * s%dt) .and. (k_no_v >1))
       t_sound_cross = t_sound_cross + (s%r(k_no_v-1)-s%r(k_no_v))/s%csound(k_no_v)
       k_no_v = k_no_v - 1 ! loop outward
    end do
  end function get_index_no_v

  subroutine extras_startup(id, restart, ierr)
    integer, intent(in) :: id
    logical, intent(in) :: restart
    integer, intent(out) :: ierr
    type (star_info), pointer :: s
    integer :: k
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
  end subroutine extras_startup

  integer function extras_start_step(id)
    integer, intent(in) :: id
    integer :: k_no_v, ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    extras_start_step = 0

    if (s% lxtra(1) .eqv. .false.) then
       if (log10(exp(maxval(s% xh(s% i_lnT, 1:s% nz)))) > 8.95d0) then
          write(*,*) "Found layer with logT>8.95"
          s% lxtra(1) = .true.
       end if
    end if

    if (s% lxtra(2) .eqv. .false.) then
       if ((s% xa(s% net_iso(io16), s% nz) <= 0.1d0) .and. &
            (s% xa(s% net_iso(ic12), s%nz) <= 1d-3) .and. &
            (s% xa(s% net_iso(ihe4), s%nz) <= 5d-3) .and. &
            (s% xa(s% net_iso(ih1), s%nz) <= 0.5d0)) then
          write(*,*) "Oxygen depletion!"
          s% lxtra(2) = .true.
          ! get some more terminal output
          s% num_trace_history_values = 2
          s% trace_history_value_name(1) = 'non_fe_core_infall'
          s% trace_history_value_name(2) = 'rel_E_err'
       end if
    end if

    if (s% lxtra(3) .eqv. .false.) then
       if ((s% xa(s% net_iso(isi28), s% nz) <= 5d-3) .and. &
            (s% xa(s% net_iso(io16), s%nz) <= 5d-3) .and. &
            (s% xa(s% net_iso(ic12), s%nz) <= 5d-3) .and. &
            (s% xa(s% net_iso(ihe4), s%nz) <= 0.2d0) .and. &
            (s% xa(s% net_iso(ih1), s%nz) <= 0.5d0)) then
          write(*,*) "Silicon depletion!"
          s% lxtra(3) = .true.
          ! get some more terminal output
          s% num_trace_history_values = 4
          s% trace_history_value_name(1) = 'Fe_core'
          s% trace_history_value_name(2) = 'fe_core_infall'
          s% trace_history_value_name(3) = 'non_fe_core_infall'
          s% trace_history_value_name(4) = 'rel_E_err'
          ! force saving profiles
          s% write_profiles_flag = .true.
          s% profile_interval = 1
       end if
    end if
    k_no_v = get_index_no_v(id, ierr)
    if (k_no_v > 1) then
       ! set new velocity_q_upper_boundx for current timestep
       s% velocity_q_upper_bound = s%q(k_no_v)
    else
       ! reset dummy limit
       s% velocity_q_upper_bound = 1d99
    end if
  end function extras_start_step

  ! returns either keep_going, retry, backup, or terminate.
  integer function extras_check_model(id)
    integer, intent(in) :: id
    integer :: ierr, k
    real(dp) :: dlnL_dt, dlnTeff_dt, dlnR_dt
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    extras_check_model = keep_going

    ! nasty numerical spikes occur at constant R
    ! check for large dL/dt and/or dTeff/dt at small dR/dt
    ! and retry if you find one
    dlnL_dt = (log(s%xh(s%i_lum, 1)) - log(s%xh_old(s%i_lum, 1)))/s%dt
    dlnTeff_dt = (s%xh(s%i_lnT, 1) - s%xh_old(s%i_lnT, 1))/s%dt
    dlnR_dt =  (s%xh(s%i_lnR, 1) - s%xh_old(s%i_lnR, 1))/s%dt

    ! the control below should be ~0 because of the black body relation
    s% xtra(1) = (dlnL_dt - 4*dlnTeff_dt)/dlnR_dt - 2.0d0

    ! ! if max logT>8.95 and deviation from BB dev larger than x_ctrl(4) retry
    ! if (s%lxtra(1) .and. abs(s%xtra(1)) >= s%x_ctrl(4)) then
    !        print *, "test",  s%xtra(1), "large!RETRY"
    !        extras_check_model = retry
    ! end if

    if (extras_check_model == terminate) s% termination_code = t_extras_check_model
  end function extras_check_model

  integer function how_many_extra_history_columns(id)
    integer, intent(in) :: id
    integer :: ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    how_many_extra_history_columns = 4
  end function how_many_extra_history_columns

  subroutine data_for_extra_history_columns(id, n, names, vals, ierr)
    integer, intent(in) :: id, n
    character (len=maxlen_history_column_name) :: names(n)
    real(dp) :: vals(n)
    integer, intent(out) :: ierr
    type (star_info), pointer :: s
    integer :: k
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return

    ! find location above which we damp v
    k = get_index_no_v(id, ierr)
    names(1) = 'k_no_v_above'
    vals(1) = k
    names(2) = 'q_no_v_above'
    vals(2) = s%q(k)
    names(3) = 'tau_no_v_above'
    vals(3) = s%tau(k)
    names(4) = 'BB_numerical_deviation'
    vals(4) = s%xtra(1)

  end subroutine data_for_extra_history_columns

  integer function how_many_extra_profile_columns(id)
    integer, intent(in) :: id
    integer :: ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    how_many_extra_profile_columns = 0
  end function how_many_extra_profile_columns

  subroutine data_for_extra_profile_columns(id, n, nz, names, vals, ierr)
    integer, intent(in) :: id, n, nz
    character (len=maxlen_profile_column_name) :: names(n)
    real(dp) :: vals(nz,n)
    integer, intent(out) :: ierr
    type (star_info), pointer :: s
    integer :: k
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
  end subroutine data_for_extra_profile_columns


  integer function how_many_extra_history_header_items(id)
    integer, intent(in) :: id
    integer :: ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    how_many_extra_history_header_items = 0
  end function how_many_extra_history_header_items


  subroutine data_for_extra_history_header_items(id, n, names, vals, ierr)
    integer, intent(in) :: id, n
    character (len=maxlen_history_column_name) :: names(n)
    real(dp) :: vals(n)
    type(star_info), pointer :: s
    integer, intent(out) :: ierr
    ierr = 0
    call star_ptr(id,s,ierr)
    if(ierr/=0) return
  end subroutine data_for_extra_history_header_items


  integer function how_many_extra_profile_header_items(id)
    integer, intent(in) :: id
    integer :: ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    how_many_extra_profile_header_items = 0
  end function how_many_extra_profile_header_items


  subroutine data_for_extra_profile_header_items(id, n, names, vals, ierr)
    integer, intent(in) :: id, n
    character (len=maxlen_profile_column_name) :: names(n)
    real(dp) :: vals(n)
    type(star_info), pointer :: s
    integer, intent(out) :: ierr
    ierr = 0
    call star_ptr(id,s,ierr)
    if(ierr/=0) return
  end subroutine data_for_extra_profile_header_items


  ! returns either keep_going or terminate.
  ! note: cannot request retry or backup; extras_check_model can do that.
  integer function extras_finish_step(id)
    integer, intent(in) :: id
    real(dp) :: m_infall
    integer :: ierr, k, k_sonic
    character (len=200) :: fname
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
    extras_finish_step = keep_going

    if ((s% lxtra(1) .eqv. .true.) .and. &
         (s% lxtra(11) .eqv. .false.)) then
       s% lxtra(11) = .true. ! avoid getting in here again
       print *, "save first timestep for max(T)>10^8.95K"
       write(fname, fmt="(a15)") 'CHE_logT895.mod'
       call star_write_model(id, fname, ierr)
       write(fname, fmt="(a17)") 'CHE_logT895.photo'
       call star_write_photo(id, trim(s%photo_directory)//'/'//trim(fname), ierr)
       write(fname, fmt="(a16)") 'CHE_logT895.data'
       call star_write_profile_info(id, trim(s%log_directory)//'/'//trim(fname), ierr)
    end if

    if ((s%lxtra(2) .eqv. .true.) .and. &
        (s% lxtra(12) .eqv. .false.)) then
       s% lxtra(12) = .true. ! avoid getting in here again
       print *, "save first timestep post O core depletion"
       write(fname, fmt="(a10)") 'O_depl.mod'
       call star_write_model(id, fname, ierr)
       write(fname, fmt="(a12)") 'O_depl.photo'
       call star_write_photo(id, trim(s%photo_directory)//'/'//trim(fname), ierr)
       write(fname, fmt="(a11)") 'O_depl.data'
       call star_write_profile_info(id, trim(s%log_directory)//'/'//trim(fname), ierr)
       ! save more output
       s% photo_interval = 100
       s% pg% pgstar_interval = 10
       s% terminal_interval = 1
       s% write_header_frequency = 1
       s% profile_interval = 1
    end if

    if ((s%lxtra(3) .eqv. .true.) .and. &
        (s% lxtra(13) .eqv. .false.)) then
       s% lxtra(13) = .true. ! avoid getting in here again
       print *, "save first timestep post Si core depletion"
       write(fname, fmt="(a11)") 'Si_depl.mod'
       call star_write_model(id, fname, ierr)
       write(fname, fmt="(a13)") 'Si_depl.photo'
       call star_write_photo(id, trim(s%photo_directory)//'/'//trim(fname), ierr)
       write(fname, fmt="(a12)") 'Si_depl.data'
       call star_write_profile_info(id, trim(s%log_directory)//'/'//trim(fname), ierr)
       ! save more output
       s% photo_interval = 50
       s% pg% pgstar_interval = 1
       s% terminal_interval = 1
       s% write_header_frequency = 1
       s% profile_interval = 1
       s% pg% Profile_Panels5_file_flag = .true.
    end if

    ! post Si depletion, check velocity
    if ((s%lxtra(13) .eqv. .true.) .and. &
        (s% fe_core_mass > 0.0d0)) then
       k = s%nz
       do while (s% m(k) <= s% fe_core_mass * Msun)
          k = k-1 ! loop outwards
       end do
       ! k is now the outer index of the fe core
       if (maxval(abs(s%v(k:s%nz))) >= s% fe_core_infall_limit) then
          s% termination_code = t_fe_core_infall_limit
          write(*, '(/,a,/, 99e20.10)') &
               'stop because fe_core_infall > fe_core_infall_limit', &
               s% fe_core_infall, s% fe_core_infall_limit
          print *, "treshold v used", maxval(abs(s%v(k:s%nz)))
          extras_finish_step = terminate
       end if
    end if

  end function extras_finish_step


  subroutine extras_after_evolve(id, ierr)
    integer, intent(in) :: id
    integer, intent(out) :: ierr
    type (star_info), pointer :: s
    ierr = 0
    call star_ptr(id, s, ierr)
    if (ierr /= 0) return
  end subroutine extras_after_evolve


end module run_star_extras
