// Auto-generated. Do not edit.

use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct BackupTarget {
    pub protocol: String,

    pub url: String,

    pub bucketname: String,

    pub path: String,

    pub accesskey: String,

    pub secretkey: String,

}