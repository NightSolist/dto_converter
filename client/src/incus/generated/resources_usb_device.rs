// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};
use crate::incus::ResourcesUSBDeviceInterface;

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ResourcesUSBDevice {
    pub busaddress: u64,

    pub deviceaddress: u64,

    pub serial: String,

    pub interfaces: Vec<ResourcesUSBDeviceInterface>,

    pub vendor: String,

    pub vendorid: String,

    pub product: String,

    pub productid: String,

    pub speed: f64,

}