"""Small adaptation of pinned sentry-nodestore-s3; upstream owns read/delete/cache."""
from sentry_nodestore_s3.backend import S3PassthroughDjangoNodeStorage
from retention import expiry


class ExpiringNodeStorage(S3PassthroughDjangoNodeStorage):
    def _set_bytes(self, id, data, ttl=None):
        if self.write_through:
            raise ValueError('write-through is unsupported for this expiry backend')
        key = self._S3PassthroughDjangoNodeStorage__get_key_for_id(id, self.object_sharding)
        encoding = ''
        if self.compression is not None:
            compressed = self.compression_strategies[self.compression].encode(data)
            if len(compressed) <= len(data):
                data, encoding = compressed, self.compression
        # Node IDs are immutable. Keep original expiry if a node is rewritten.
        try:
            metadata = self.client.head_object(Bucket=self.bucket_name, Key=key).get('Metadata', {})
        except self.client.exceptions.ClientError as error:
            if error.response['ResponseMetadata']['HTTPStatusCode'] != 404:
                raise
            metadata = {'expires-at': expiry(ttl)}
        self.client.put_object(Bucket=self.bucket_name, Key=key, Body=data,
                               ContentEncoding=encoding, Metadata=metadata)
