pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721Full.sol";

contract CarRegistry is ERC721Full {
    constructor() public ERC721Full("ArtRegistryToken", "ART") {}

    struct QRCode {
        string name;
        string vin;
        string make;
        string model;
        string year;
        string color;
        string url;
    }

    mapping(uint256 => QRCode) public vehicleCollection;
    
    function registerOwner(
        address owner,
        string memory name,
        string memory vin,
        string memory make,
        string memory model,
        string memory year,
        string memory color,
        string memory url
    ) 
    
    public returns (uint256) {
        uint256 tokenId = totalSupply();

        _mint(owner, tokenId);
       
        _setTokenURI(tokenId, url);

        vehicleCollection[tokenId] = QRCode(name, vin, make, model, year, color,  url);

        return tokenId;
    }


    }