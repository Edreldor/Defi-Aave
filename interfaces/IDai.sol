pragma solidity =0.5.12;

interface IDai {
    function balanceOf(address owner) external view returns (uint256 balance);
}
