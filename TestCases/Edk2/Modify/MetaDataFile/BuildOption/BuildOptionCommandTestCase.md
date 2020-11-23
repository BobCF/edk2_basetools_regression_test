- For "FD_SIZE_2MB"    pass
  - build -p OvmfPkg\OvmfPkgIa32X64.dsc -a X64 -a IA32 -t VS2015x86 -b RELEASE
  - build -p OvmfPkg\OvmfPkgIa32X64.dsc -a X64 -a IA32 -t VS2015x86 -b RELEASE -D FD_SIZE_2MB
- For "-D NETWORK_TLS_ENABLE=TRUE" pass (with deletion issue, need"type: manual")
  - build -p OvmfPkg\OvmfPkgIa32X64.dsc -a X64 -a IA32 -t VS2015x86 -b RELEASE
  - build -p OvmfPkg\OvmfPkgIa32X64.dsc -a X64 -a IA32 -t VS2015x86 -b RELEASE -D NETWORK_TLS_ENABLE=TRUE
- For "CSM_ENABLE"   pass
  - build -p TestPkg\TestPkg32X64.dsc -a X64 -a IA32 -t VS2015x86 -b RELEASE
  - build -p TestPkg\TestPkg32X64.dsc -a X64 -a IA32 -t VS2015x86 -b RELEASE -D CSM_ENABLE
  - PS:  Change first to second
    - !ifdef $(CSM_ENABLE)
            NULL|TestPkg/Csm/LegacyBootManagerLib/LegacyBootManagerLib.inf
            NULL|TestPkg/Csm/LegacyBootMaintUiLib/LegacyBootMaintUiLib.inf
    - !ifdef $(CSM_ENABLE)
            NULL|OvmfPkg/Csm/LegacyBootManagerLib/LegacyBootManagerLib.inf
            NULL|OvmfPkg/Csm/LegacyBootMaintUiLib/LegacyBootMaintUiLib.inf
