from pathlib import Path
import os
import logging
from pprint import pprint
from pipeline.infra.rclone import RcloneWorker
from ui.components.extensions.progress_dialog import ProgressDialog
from .base import Step

logger = logging.getLogger(__name__)

class CopyLocalOutFileStep(Step):
    """
    Step: asynchronously copy the work and preview work file to local 04_Out folder.
    Keeps a reference to the RcloneWorker in page.active_workers
    so that it doesn't get garbage-collected mid flight.
    """

    def execute(self, ctx: dict, callback):
        page                = ctx["page"]
        message_box_title   = ctx["process_title"] + " : Copy Local Out File Step"

        local_work_file     = ctx["working_version"]["work_detail"]["file_name"]
        local_preview_file  = Path(ctx["preview_file_path"]).name

        local_work_path     = Path(ctx["working_version"]["work_detail"]["work_file"])
        local_preview_path  = Path(ctx["preview_file_path"])
        local_publish_path  = Path(ctx["local_publish_dir"])
        server_publish_path = Path(ctx["server_publish_dir"])

        dialog = page._active_dialog

        def copy_approved_work_file():

            # STEP 1: 
            print(f"\n --- Copying published files to local 04_Out folder \n")
            worker = RcloneWorker("copyto", local_work_path.as_posix(), Path(local_publish_path / local_work_file).as_posix(), flags=["--update"])
            page.active_workers.append(worker)
            
            def on_finished(status_code):
                if worker in page.active_workers:
                    page.active_workers.remove(worker)
                # Proceed to copy the next file in list
                copy_approved_preview_file(status_code)

            dialog.canceled.connect(worker.cancel)
            worker.progress_signal.connect(page._on_copy_progress)
            worker.finished_signal.connect(on_finished)
            worker.start()
            dialog.show()

            # If you have an active dialog for progress
            if page._active_dialog:
                page._active_dialog.label.setText("Copying Approved Work File (local)...")
                page._active_dialog.progress_bar.setValue(0)

        def copy_approved_preview_file(prev_step_status_code):
            if prev_step_status_code != 0:
                logger.error("Approved Work file copy failed. Aborting publish sequence !")
                if callback:
                    callback(prev_step_status_code)
                return

            # STEP 2: Copy approved preview file from 02_Preview to 04_Out (local copy)
            worker = RcloneWorker("copyto", local_preview_path.as_posix(), Path(local_publish_path / local_preview_file).as_posix(), flags=["--update"])
            # dialog = page._active_dialog
            page.active_workers.append(worker)
            
            def on_finished(status_code):
                if worker in page.active_workers:
                    page.active_workers.remove(worker)
                # Proceed to copy the next file in list
                copy_publish_folder(status_code)

            dialog.canceled.connect(worker.cancel)
            worker.progress_signal.connect(page._on_copy_progress)
            worker.finished_signal.connect(on_finished)
            worker.start()
            dialog.show()

            # If you have an active dialog for progress
            if page._active_dialog:
                page._active_dialog.label.setText("Copying Approved Preview File (local)...")
                page._active_dialog.progress_bar.setValue(0)

        def copy_publish_folder(prev_step_status_code):
            if prev_step_status_code != 0:
                logger.error("Approved Preview file copy failed. Aborting publish sequence !")
                if callback:
                    callback(prev_step_status_code)
                return
            
            # STEP 3: 
            print(f"\n --- Copying published files to from local to server \n")
            worker = RcloneWorker("sync", local_publish_path.as_posix(), server_publish_path.as_posix(), flags=["--update"])
            # dialog = page._active_dialog
            page.active_workers.append(worker)
            
            def on_finished(status_code):
                logger.debug(f"Copy Local Out File Step is Finished :{status_code}")    
                if worker in page.active_workers:
                    page.active_workers.remove(worker)

                if status_code == 0:
                    pass
                else:
                    error = dict()
                    error["error_code"] = status_code
                    error["message"]    = f"Copy Local Out File Step failed."
                    page.exception_messages.append(error)    

                callback(status_code)

            dialog.canceled.connect(worker.cancel)
            worker.progress_signal.connect(page._on_copy_progress)
            worker.finished_signal.connect(on_finished)
            worker.start()
            dialog.show()

            # If you have an active dialog for progress
            if page._active_dialog:
                page._active_dialog.label.setText("Copying Publish Directory to Server...")
                page._active_dialog.progress_bar.setValue(0)
        
        copy_approved_work_file()

class CopyWorkFileStep(Step):
    """
    Step: asynchronously copy the current work file to the server.
    Keeps a reference to the RcloneWorker in page.active_workers
    so that it doesn't get garbage-collected mid flight.
    """

    def execute(self, ctx: dict, callback):
        page = ctx["page"]
        current_working_version = ctx["working_version"]
        message_box_title   = ctx["process_title"] + " : Copy Work File Step"

        filename    = current_working_version["work_detail"]["file_name"]
        local_file  = current_working_version["work_detail"]["work_file"]
        remote_file = Path(current_working_version["ftp_work_directory"]) / filename

        print(f"\n --- Uploading Work file to server : {local_file}\n")
        worker      = RcloneWorker("copyto", str(local_file), str(remote_file), ["--update"])

        page.active_workers.append(worker)

        worker.progress_signal.connect(page._on_copy_progress)


        def _on_finished(status_code):

            logger.debug(f"CopyWorkFileStep {filename} is Finished :{status_code}")    
            if worker in page.active_workers:
                page.active_workers.remove(worker)

            if status_code == 0:
                pass
            else:
                error = dict()
                error["error_code"] = status_code
                error["message"]    = f"Work file {filename} copy failed."
                page.exception_messages.append(error)    

            callback(status_code)

        worker.finished_signal.connect(_on_finished)
        worker.start()

        if page._active_dialog:
            page._active_dialog.label.setText(f"Copying Work File {filename} ...")
            page._active_dialog.progress_bar.setValue(0)


class CopyPreviewFileStep(Step):
    """
    Step: asynchronously copy the current task Preview file to the server.
    Keeps a reference to the RcloneWorker in page.active_workers
    so that it doesn't get garbage-collected mid flight.
    
    """

    def execute(self, ctx, callback):

        # print("Inside CopyPreviewFileStep")

        page                    = ctx["page"]
        current_working_version = ctx["working_version"]
        filename                = current_working_version["work_detail"]["file_name"]
        preview_file_name, _    = os.path.splitext(filename)

        preview_file_path      = ctx["preview_file_path"]
        
        remote_file            = Path(current_working_version["ftp_preview_directory"]) / preview_file_path.name

        # page.preview_file_path = preview_file_path


        # worker               = RcloneWorker("copyto", str(preview_file_path), str(remote_file), ["--update"])
        print(f"\n --- Uploading Preview file to server : {preview_file_path}\n")
        worker               = RcloneWorker("copyto", preview_file_path.as_posix(), remote_file.as_posix(), ["--update"] )

        page.active_workers.append(worker)


        worker.progress_signal.connect(page._on_copy_progress)

        def on_finished(status_code):
            logger.debug(f"CopyPreviewFileStep {preview_file_path.name} is Finished :{status_code}")
            if worker in page.active_workers:
                page.active_workers.remove(worker)


            if status_code == 0:
                pass
            else:
                error = dict()
                error["error_code"] = status_code
                error["message"]    = f"Work file {preview_file_path.name} copy failed."
                page.exception_messages.append(error)    

            callback(status_code)

        worker.finished_signal.connect(on_finished)
        worker.start()

        if page._active_dialog:
            page._active_dialog.label.setText(f"Copying Preview File {preview_file_path.name} ...")
            page._active_dialog.progress_bar.setValue(0)


            # logger.debug()


class CopyPublishFilesStep(Step):

    """
    Step: asynchronously copy the current task file(s) to the server.
    Keeps a reference to the RcloneWorker in page.active_workers
    so that it doesn't get garbage-collected mid flight.
    """
    def execute(self, ctx, callback):
        # print("Inside CopyPublishFilesStep")
        page                  = ctx["page"]
        current_working_version = ctx["working_version"]

        # print("line 236")
        # pprint(current_working_version)

        local_output_location = Path(current_working_version["local_output_directory"])
        ftp_output_location   = Path(current_working_version["ftp_output_directory"])

        local_input_location  = Path(current_working_version["input_directory"])
        ftp_input_location    = Path(current_working_version["ftp_input_directory"])

        # The local work file we'll copy to "output_tasks_work_location"
        src_file               = current_working_version["work_detail"]["work_file"]
        output_tasks_locations = current_working_version.get("output_tasks_work_location", [])
        
        # print("line 250")    

        # If local_output_location doesn't exist, we won't even try to copy it
        # but we'll still proceed to the next steps.
        def copy_output_folder():
            # print("line 255")

            # print("copy_output_folder got called")
            if not local_output_location.exists():
                logger.info(f"[Publish] Output folder '{local_output_location}' does not exist, skipping step.")
                # Skip to copying input
                copy_input_folder(0)
                return
            # print("line 258")
            # STEP 1: Copy local_output_location -> ftp_output_location
            print(f"\n --- Uploading 04_Out folder to server : {local_output_location}\n")
            worker = RcloneWorker("copy", str(local_output_location), str(ftp_output_location), flags=["--update"])
            # print("line 261")
            # worker = RcloneWorker("copyto", str(preview_file_path), str(remote_file), ["--update"])
            page.active_workers.append(worker)

            worker.progress_signal.connect(page._on_copy_progress)

            def on_finished(status_code):
                logger.debug(f"[Publish] Output folder copy finished with code {status_code}")
                if worker in page.active_workers:
                    page.active_workers.remove(worker)

                # Proceed to copy input folder next
                copy_input_folder(status_code)

            worker.finished_signal.connect(on_finished)
            worker.start()

            # If you have an active dialog for progress
            if page._active_dialog:
                page._active_dialog.label.setText("Copying Output Folder...")
                page._active_dialog.progress_bar.setValue(0)

        def copy_input_folder(prev_step_status_code):
            # print("copy_input_folder got called")
            # If the output folder copy failed, skip everything
            if prev_step_status_code != 0:
                logger.error("[Publish] Output folder copy failed. Aborting publish sequence.")
                if callback:
                    callback(prev_step_status_code)
                return

            # STEP 2: Copy local_input_location -> ftp_input_location
            # worker = RcloneWorker(command="copy",source=str(local_input_location),destination=str(ftp_input_location),flags=["--update"])
            # worker = RcloneWorker("copy", str(local_input_location), str(ftp_input_location) ,flags=["--update"])
            print(f"\n --- Uploading 00_Input folder to server : {local_input_location}\n")
            worker = RcloneWorker("copy", local_input_location.as_posix(), ftp_input_location.as_posix(), flags=["--update"])
            page.active_workers.append(worker)

            worker.progress_signal.connect(page._on_copy_progress)

            def on_finished(status_code):
                logger.debug(f"[Publish] {local_input_location.as_posix()} Input folder copy finished with code {status_code}")
                if worker in page.active_workers:
                    page.active_workers.remove(worker)

                # Move on to copying the work file to each location
                copy_work_file_to_output_locations(status_code)

            worker.finished_signal.connect(on_finished)
            worker.start()

            if page._active_dialog:
                page._active_dialog.label.setText(f"Copying {local_input_location.as_posix()} Input Folder...")
                page._active_dialog.progress_bar.setValue(0)

        def copy_work_file_to_output_locations(prev_step_status_code):  
            # If the input folder copy failed, skip everything
            # print("line 322")
            # print("copy_work_file_to_output_locations")
            # print(prev_step_status_code)

            if prev_step_status_code != 0:
                logger.error(f"[Publish] {local_input_location.as_posix()} Input folder copy failed. Aborting publish sequence.")
                
                if callback:
                    callback(prev_step_status_code)
                return

            if not src_file:
                logger.error(f"[Publish] No source file {os.path.basename(src_file)} provided for output_tasks_work_location.")
                
                if callback:
                    callback(-1)
                return

            # We'll define an iterator over output_tasks_locations
            # and copy the src_file to each location in sequence.
            # pprint(output_tasks_locations)
            locations_iter = iter(output_tasks_locations)
            # print("line 342")
            # print(locations_iter)


            def copy_next_location():
                try:
                    output_location = next(locations_iter)
                    # print(output_location)
                except StopIteration:
                    # No more locations left, we are done
                    logger.info("[Publish] Done copying work file to all output tasks.")
                    if callback:
                        callback(0)  # success
                    return

                ftp_work_dir = output_location.get("ftp_work_directory").replace("\\", "/")
                # print("line 361")
                # print(ftp_work_dir)
                if not ftp_work_dir:
                    logger.warning(f"[Publish] {ftp_work_dir} ftp_work_directory is missing in output_tasks_work_location entry. Skipping.")
                    copy_next_location()
                    return

                worker = RcloneWorker("copyto", str(src_file), str(Path(ftp_work_dir)), flags=["--update"])
                page.active_workers.append(worker)

                worker.progress_signal.connect(page._on_copy_progress)

                def on_finished(status_code):
                    logger.debug(f"[Publish] Copying work file {os.path.basename(src_file)} to '{ftp_work_dir}' finished with code {status_code}")
                    if worker in page.active_workers:
                        page.active_workers.remove(worker)
                    # Proceed to next location regardless of success/failure (customize as needed)
                    copy_next_location()

                worker.finished_signal.connect(on_finished)
                worker.start()

                if page._active_dialog:
                    page._active_dialog.label.setText(f"Copying work file to {ftp_work_dir}...")
                    page._active_dialog.progress_bar.setValue(0)
            copy_next_location()        
        copy_output_folder()            