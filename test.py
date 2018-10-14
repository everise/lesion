import os
import glob
from impl_rena import ImplReNA

study_dir = 'sample_data_deeksha'
nsub = 5
subno = 0
dirlist = glob.glob(study_dir + '/TBI*')
for subj in dirlist:
    t1file = os.path.join(subj, 'T1.nii.gz')
    t2file = os.path.join(subj, 'T2.nii.gz')
    fl = os.path.join(subj, 'FLAIR.nii.gz')
    fileArr = [t1file, t2file, fl]

    if not (os.path.isfile(t1file) and os.path.isfile(t2file)
            and os.path.isfile(fl)):
        continue

    if subno < nsub:
        subno = subno + 1
        print("subject %d " % (subno))
    else:
        break

    for file_address in fileArr:
        impl = ImplReNA(file_address)
        n_samples, n_x, n_y, n_z = impl.data_info()
        print('number of samples: %i, \nDimensions n_x: %i, n_y: %i, n_z: %i' % (n_samples, n_x, n_y, n_z))

        to_ward, to_rena = impl.get_connectivity()
        print('Time Ward: %0.3f, Time ReNA: %0.3f' % (to_ward, to_rena))

        store_subj_dir = file_address.split('\\')[-2:-1][0]
        store_file_dir = file_address.split('\\')[-1:][0].split('.')[:1][0]
        store_dir = os.path.join('figures', store_subj_dir, store_file_dir)
        impl.storefig(store_dir)
