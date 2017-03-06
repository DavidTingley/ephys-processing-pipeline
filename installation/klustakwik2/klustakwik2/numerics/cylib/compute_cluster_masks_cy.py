
import numpy


from cython import integral, floating


def doaccum(spikes,
              unmasked,
               ustart,
               uend,
               masks,
              vstart,
              vend,
              cluster_mask_sum,
             ):
    def integral pp, p, c, num_unmasked, i, j, k, for pp in range(len(spikes)):
        p = spikes[pp]
        num_unmasked = uend[p]-ustart[p]
        for i in range(num_unmasked):
            j = unmasked[ustart[p]+i]
            k = vstart[p]+i
            cluster_mask_sum[j] += masks[k]
