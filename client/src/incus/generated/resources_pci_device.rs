// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesPCIVPD;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesPCIDevice {
    pub driver: String,

    pub driverversion: String,

    pub numanode: u64,

    pub pciaddress: String,

    pub vendor: String,

    pub vendorid: String,

    pub product: String,

    pub productid: String,

    pub iommugroup: u64,

    pub vpd: ResourcesPCIVPD,

}