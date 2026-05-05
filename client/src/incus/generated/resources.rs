// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesCPU;
use crate::incus::ResourcesGPU;
use crate::incus::ResourcesLoad;
use crate::incus::ResourcesMemory;
use crate::incus::ResourcesNetwork;
use crate::incus::ResourcesPCI;
use crate::incus::ResourcesSerial;
use crate::incus::ResourcesStorage;
use crate::incus::ResourcesSystem;
use crate::incus::ResourcesUSB;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Resources {
    pub cpu: ResourcesCPU,

    pub memory: ResourcesMemory,

    pub gpu: ResourcesGPU,

    pub network: ResourcesNetwork,

    pub storage: ResourcesStorage,

    pub usb: ResourcesUSB,

    pub pci: ResourcesPCI,

    pub system: ResourcesSystem,

    pub load: ResourcesLoad,

    pub serial: ResourcesSerial,

}