def processJobs(): 
    import objaverse
    objaverse.__version__

    uids = objaverse.load_uids()

    annotations = objaverse.load_annotations(uids)
    annotations[uids[0]]

    import multiprocessing
    processes = multiprocessing.cpu_count()
    processes

    #Filtering the annotations to extract only the ones with by license
    cc_by_uids = [uid for uid, annotation in annotations.items() if annotation["license"] == "by" or annotation["license"] == "by-sa"]
    cc_by_uids[:150]

    #Selecting UIDS randomly
    import random

    random.seed(1111)

    random_object_uids = random.sample(cc_by_uids, 500)

    random_object_uids

    objects = objaverse.load_objects(
        uids=random_object_uids,
        download_processes=processes
    )
    
    print(objects[0])
if __name__ == '__main__':
    processJobs()