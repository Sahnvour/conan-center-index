from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, download
import os


class wgpu_nativeConanfile(ConanFile):
    name = "wgpu_native"
    description = "Native WebGPU implementation based on wgpu-core"
    license = "MIT OR Apache-2.0"
    homepage = "https://github.com/gfx-rs/wgpu-native"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("webgpu", "wgpu", "gpu", "graphics", "rendering", "3d", "2d")

    settings = "os", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}


    def validate(self):
        os = self.settings.os
        if os not in ("Linux", "Windows", "Macos"):
            raise ConanInvalidConfiguration(f"No prebuilt binaries exist for your OS ({os})")

        arch = self.settings.arch
        if arch not in ("x86_64", "armv8"):
            raise ConanInvalidConfiguration(f"No prebuilt binaries exist for your architecture ({arch})")

        if os is "Windows" and arch is not "x86_64":
            raise ConanInvalidConfiguration(f"No prebuilt binaries exist for your architecture ({arch})")

        if self.settings.build_type not in ("Debug", "Release"):
            raise ConanInvalidConfiguration("Only Debug and Release build types are supported")

    def build(self):
        os = str(self.settings.os)
        arch = str(self.settings.arch)
        build_type = str(self.settings.build_type)
        get(self, **self.conan_data["sources"][self.version]["binaries"][os][arch][build_type])

        licenses = self.conan_data["sources"][self.version]["licenses"]
        download(self, filename="LICENSE.MIT", **licenses["mit"])
        download(self, filename="LICENSE.APACHE", **licenses["apache"])

    def package(self):
        copy(self, pattern="LICENSE.*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        copy(self, pattern="*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"), keep_path=False)

        patterns = ["*.so", "*.dll", "*.dylib"] if self.options.shared else ["*.a", "*.lib"]
        for p in patterns:
            copy(self, pattern=p, src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["wgpu_native"]

        if self.settings.os is "Linux":
            self.cpp_info.system_libs.extend(["m", "pthread", "dl"])
