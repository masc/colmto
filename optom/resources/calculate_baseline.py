import h5py
import numpy as np
import os

f_hdf5 = h5py.File("Scenarios_baseline_time_loss.hdf5", "a")

for i_scenario in ["HE-B49"]:
    for i_stat in ["dissatisfaction", "relative_time_loss", "time_loss"]:
        for i_type in ["alltypes", "passenger", "tractor", "truck"]:
            f_hdf5.create_dataset(
                name=os.path.join(
                    i_scenario,
                    "19000.0",
                    "best",
                    "global",
                    "driver",
                    i_type,
                    "baseline_{}".format(i_stat)
                ),
                data=np.array(
                    [
                        np.median(
                            np.array(
                                f_hdf5.get(i_scenario).get("19000.0").get("best").get("global")
                                .get("driver").get(i_type).get("{}_end".format(i_stat))
                            ).T[i]
                        )
                        for i in xrange(len(f_hdf5.get(i_scenario).get("19000.0").get("best")
                                            .get("global").get("driver").get(i_type)
                                            .get("{}_end".format(i_stat))[0]))]),
                compression="gzip",
                compression_opts=9,
                fletcher32=True,
                chunks=True
            )

f_hdf5.close()
