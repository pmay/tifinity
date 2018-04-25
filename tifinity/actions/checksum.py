import hashlib

class Checksum():

    @staticmethod
    def checksum(tiff, alg="md5"):
        hashes = {}
        hashes["full"] = Checksum._hash_data(tiff.raw_data(), alg)

        image_hashes = []
        ifd_hashes = []
        for ifd in tiff.ifds:
            image_hashes.append(Checksum._hash_data(ifd.img_data, alg))
            ifd_hashes.append(Checksum._hash_data(ifd.ifd_data, alg))
        hashes["images"] = image_hashes
        hashes["ifds"] = ifd_hashes
        return hashes

    @staticmethod
    def _hash_data(data, alg="sha256"):
        """Returns the hash value of the specified data using the specified hashing algorithm"""
        m = hashlib.new(alg)
        m.update(data)
        return m.hexdigest()