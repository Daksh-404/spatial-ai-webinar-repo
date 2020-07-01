import time
import edgeiq
"""
Use object detection to detect objects in the frame in realtime. The
types of objects detected can be changed by selecting different models.

To change the computer vision model, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_model.html

To change the engine and accelerator, follow this guide:
https://dashboard.alwaysai.co/docs/application_development/changing_the_engine_and_accelerator.html

To install app dependencies in the runtime container, list them in the requirements.txt file.
"""


def main():
    obj_detect = edgeiq.ObjectDetection(
            "alwaysai/ssd_mobilenet_v2_coco_2018_03_29")
    obj_detect.load(engine=edgeiq.Engine.DNN)

    print("Loaded model:\n{}\n".format(obj_detect.model_id))
    print("Engine: {}".format(obj_detect.engine))
    print("Accelerator: {}\n".format(obj_detect.accelerator))
    print("Labels:\n{}\n".format(obj_detect.labels))

    fps = edgeiq.FPS()

    try:
        with edgeiq.WebcamVideoStream(cam=0) as video_stream, \
                edgeiq.Streamer() as streamer:
            # Allow Webcam to warm up
            time.sleep(2.0)
            fps.start()

            # loop detection
            while True:
                distances=[]
                depth_image,color_image = video_stream.read()
                video_stream.roi(depth_image,color_image,min=None,max=0.9,shade=0) 
                results = obj_detect.detect_objects(frame, confidence_level=.6)
                frame = edgeiq.markup_image(
                        frame, results.predictions, colors=obj_detect.colors)
                for predictions in results.predictions:
                    distances.append(video_stream.compute_object_distance(prediction.box,depth_image))

                # Generate text to display on streamer
                text = ["Model: {}".format(obj_detect.model_id)]
                text.append(
                        "Inference time: {:1.3f} s".format(results.duration))
                text.append("Objects:")

                for i,prediction in enumerate(results.predictions):
                    text.append("{}: {:2.2f}% meters".format(
                        prediction.label, prediction.confidence * 100,distances[i]))

                streamer.send_data(roi, text)

                fps.update()

                if streamer.check_exit():
                    break

    finally:
        fps.stop()
        print("elapsed time: {:.2f}".format(fps.get_elapsed_seconds()))
        print("approx. FPS: {:.2f}".format(fps.compute_fps()))

        print("Program Ending")


if __name__ == "__main__":
    main()
