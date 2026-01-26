// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CIDStorage {
    mapping(string => bool) private records;

    function storeRecord(string memory cid) public {
        records[cid] = true;
    }

    function verify(string memory cid) public view returns (bool) {
        return records[cid];
    }
}
