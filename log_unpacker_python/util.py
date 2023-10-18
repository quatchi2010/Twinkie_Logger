"""command util that use for log_unpacker."""

import construct as ct


def ByteSwappedBitStruct(*subcons, **subconskw):
  """A helper function to construct the Fixex size ByteSwapped BitStruct."""
  size = subconskw.pop("__size")

  return ct.ByteSwapped(
      ct.FixedSized(size, ct.BitStruct(*subcons, **subconskw))
  )
