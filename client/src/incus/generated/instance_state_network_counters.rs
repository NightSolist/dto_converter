// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct InstanceStateNetworkCounters {
    pub bytesreceived: i64,

    pub bytessent: i64,

    pub packetsreceived: i64,

    pub packetssent: i64,

    pub errorsreceived: i64,

    pub errorssent: i64,

    pub packetsdroppedoutbound: i64,

    pub packetsdroppedinbound: i64,

}