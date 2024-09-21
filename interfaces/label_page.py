import os
import cv2
import json
import gradio as gr
from utils.handle_video import show_video_frame, get_current_frame, scale_video

class LabelPage:
    def __init__(self, visible=True):
        self.prev_page = None
        self.prev_page_button = None
        self.video = None
        self.total_frames = None
        self.net = None
        self.events = []
        self.label_page, self.current_frame, self.slider, self.label_button, self.delete_button, self.event_list, self.labels = self.label_page(visible=visible)
        
    def label_page(self, visible=True):
        label_page = gr.Group(visible=visible)
        with label_page:
        
            # Labeling Information
            with gr.Row():
                with gr.Column(scale=2, elem_classes="column-container"):
                    with gr.Row():
                        current_frame = gr.Image(label="Current Frame", height=720, width=1280)
                        
                    with gr.Row():
                        slider = gr.Slider(minimum=1, maximum=10, step=1, value=1, label="Frame Slider")
                    
                    # Forward & Backward navigations
                    with gr.Row():
                        skip_back_10_frames = gr.Button("← 10 frames")
                        skip_back_5_frames = gr.Button("← 5 frames")
                        skip_back_1_frame = gr.Button("← 1 frames")
                        skip_1_frame = gr.Button("1 frames →")
                        skip_5_frames = gr.Button("5 frames →")
                        skip_10_frames = gr.Button("10 frames →")
                        
                    with gr.Row():
                        skip_back_10s = gr.Button("← 10s")
                        skip_back_5s = gr.Button("← 5s")
                        skip_back_1s = gr.Button("← 1s")
                        skip_1s = gr.Button("1s →")
                        skip_5s = gr.Button("5s →")
                        skip_10s = gr.Button("10s →")
                        
                with gr.Column(scale=1, elem_classes="column-container"):
                    with gr.Row(elem_id="row1", elem_classes="row-container"):
                        gr.Markdown(""" ## Event Labeling""")
                    with gr.Row():
                        player = gr.Radio(["P1", "P2", "P3", "P4"], label="Player", interactive=True)
                    with gr.Row():
                        court_position = gr.Radio(["Far deuce", "Far ad", "Near ad", "Near deuce"], label="Court Position", interactive=True)
                    with gr.Row():
                        side = gr.Radio(["Forehand", "Backhand"], label="Side", interactive=True)
                    with gr.Row():
                        shot_type = gr.Radio(["Serve", "Return", "Volley", "Lob", "Smash", "Swing"], label="Shot Type", interactive=True)
                    with gr.Row():
                        shot_direction = gr.Radio(["T", "B", "W", "CC", "DL", "DM", "II", "IO"], label="Shot Direction", interactive=True)
                    with gr.Row():
                        formation = gr.Radio(["Conventional", "I-formation", "Australian", "Non-serve"], label="Formation", interactive=True)
                    with gr.Row():
                        outcome = gr.Radio(["In", "Win", "Err"], label="Outcome", interactive=True)
                    with gr.Row():
                        player_coordinates = gr.Textbox(label="Player Coordinates", visible=False)
                    with gr.Row(elem_id="row3", elem_classes="column-container"):
                        gr.Markdown("")
                    with gr.Row():
                        label_button = gr.Button("Label Event")
                    with gr.Row():
                        delete_button = gr.Button("Delete Frame")
                    with gr.Row():
                        save_button = gr.Button("Save Labels")
                    # with gr.Row(elem_id="row2", elem_classes="row-container"):
                    #     gr.Markdown("")
                    
                    # Store labels here
                    labels = [player, court_position, side, shot_type, shot_direction, formation, outcome, player_coordinates]
            
            event_list = gr.Code(value=None, label="Labeled Events", language="json")
            save_status = gr.Textbox(label="Save Status", value="Not Saved")
            self.prev_page_button = gr.Button("Back to Net", visible=False)
            slider.release(self.update_frame, inputs=[slider], outputs=[current_frame, slider] + labels) # set up slider to update frame
            
            # Backward navigation
            skip_back_1_frame.click(self.skip_frames, inputs = [gr.Number(-1, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_back_5_frames.click(self.skip_frames, inputs = [gr.Number(-5, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_back_10_frames.click(self.skip_frames, inputs = [gr.Number(-10, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_back_1s.click(self.skip_seconds, inputs = [gr.Number(-1, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_back_5s.click(self.skip_seconds, inputs = [gr.Number(-5, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_back_10s.click(self.skip_seconds, inputs = [gr.Number(-10, visible=False), slider], outputs=[current_frame, slider] + labels)

        
            # Forward navigation
            skip_1_frame.click(self.skip_frames, inputs = [gr.Number(1, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_5_frames.click(self.skip_frames, inputs = [gr.Number(5, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_10_frames.click(self.skip_frames, inputs = [gr.Number(10, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_1s.click(self.skip_seconds, inputs = [gr.Number(1, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_5s.click(self.skip_seconds, inputs = [gr.Number(5, visible=False), slider], outputs=[current_frame, slider] + labels)
            skip_10s.click(self.skip_seconds, inputs = [gr.Number(10, visible=False), slider], outputs=[current_frame, slider] + labels)
            
            
            # Labeling
            current_frame.select(self.handle_image_click, outputs=[court_position, player_coordinates])
            label_button.click(self.label_event, inputs=labels + [slider], outputs=[event_list, save_status])
            save_button.click(self.save_labels, inputs=[event_list], outputs=[save_status])
            delete_button.click(self.delete_event, inputs=[slider], outputs=[event_list, save_status])
            
        return label_page, current_frame, slider, label_button, delete_button, event_list, labels

    def setup_prev_page_button(self, label_net_page):
        self.prev_page = label_net_page
        self.prev_page_button.click(
            self.show_label_net_page, 
            inputs=[],
            outputs=[self.label_page, self.prev_page_button, label_net_page.label_net_page, label_net_page.prev_page_button, label_net_page.next_page_button]
        )
    
    def show_label_net_page(self):
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)
    
    def update_frame(self, slider):
        frame = get_current_frame(self.video, slider)
        return frame, slider, gr.update(value=None), gr.update(value=None), gr.update(value=None), gr.update(value=None), gr.update(value=None), gr.update(value=None), gr.update(value=None), gr.update(value=None)

    def skip_frames(self, num_frames, slider):
        try:
            new_frame_index = max(1, min(slider + num_frames, self.total_frames))
            return self.update_frame(new_frame_index)
        except Exception as e:
            gr.Warning(f"Encountered an error while skipping frames: {e}")

    def skip_seconds(self, num_seconds, slider):
        try:
            fps = self.video.get(cv2.CAP_PROP_FPS)
            return self.skip_frames(int(num_seconds * fps), slider)

        except Exception as e:
            gr.Warning(f"Encountered an error while skipping frames: {e}")
    
    
    def label_event(self, player, court_position, side, shot_type, shot_direction, formation, outcome, player_coordinates, slider):
        if not player: gr.Warning("Please select a player."); return gr.update(), gr.update()
        if not court_position: gr.Warning("Please select a court position."); return gr.update(), gr.update()
        if not side: gr.Warning("Please select a side."); return gr.update(), gr.update()
        if not shot_type: gr.Warning("Please select a shot type."); return gr.update(), gr.update()
        if not shot_direction: gr.Warning("Please select a shot direction."); return gr.update(), gr.update()
        if not formation: gr.Warning("Please select a formation."); return gr.update(), gr.update()
        if not outcome: gr.Warning("Please select an outcome."); return gr.update(), gr.update()
        if not player_coordinates: gr.Warning("Please click the player on the image (hit coordinates)"); return gr.update(), gr.update()
        if formation != 'Non-serve' and shot_type != 'Serve': gr.Warning("Formation should be 'Non-serve' for non-serve shots."); return gr.update(), gr.update()
        if formation == 'Non-serve' and shot_type == 'Serve': gr.Warning("Formation should not be 'Non-serve' for serve shots."); return gr.update(), gr.update()
    
        coarse_label = f"{player}_{court_position.lower().replace(' ', '_')}_{side.lower()}_{shot_type.lower()}_{shot_direction.lower()}_{formation.lower()}_{outcome.lower()}"
    
        # Check if there's an existing event for this frame
        existing_event_index = next((index for (index, d) in enumerate(self.events) if d["frame"] == slider), None)
    
        if existing_event_index is not None:
            # Update existing event
            self.events[existing_event_index] = {
                "frame": slider,
                "event": coarse_label,
                "relative_player_width": eval(player_coordinates)[0]/1280,
                "relative_player_height": eval(player_coordinates)[1]/720,
            }
        else:
            # Add new event
            self.events.append({
                "frame": slider,
                "event": coarse_label,
                "relative_player_width": eval(player_coordinates)[0]/1280,
                "relative_player_height": eval(player_coordinates)[1]/720,
            })
    
        # Sort events by frame number
        self.events.sort(key=lambda x: x["frame"])
        
        current_video_id = self.prev_page.video_path.split("/")[-1].split(".")[0]
        return self.update_event_list()

    def update_event_list(self):
        current_video_id = self.prev_page.video_path.split("/")[-1].split(".")[0]
        events_json = json.dumps({"video_id": current_video_id, "total_frames": self.total_frames, "events": self.events}, indent=2)
        return gr.update(value=events_json, language="json"), gr.update(value="Labelled events not updated")
    
    def delete_event(self, slider):
        # Check for event index
        print(f'Deleting: frame {slider} from {self.events}')
        existing_event_index = next((index for (index, d) in enumerate(self.events) if d["frame"] == slider), None)
        if existing_event_index is None: gr.Warning("Event is not labelled"); return gr.update(), gr.update()
        self.events.pop(existing_event_index)
        return self.update_event_list()
        

    def save_labels(self, event_list):
        if not event_list: gr.Warning("No events to save."); return None
        current_video_id = self.prev_page.video_path.split("/")[-1].split(".")[0]
        os.makedirs("labelled", exist_ok=True)
        file_path = os.path.join("data", "labelled", f"{current_video_id}.json")
        
        with open(file_path, 'w') as f:
            json.dump(json.loads(event_list), f, indent=2)
        
        return gr.update(value=f"Saved to {file_path}")
    
    def load_event_list(self, video_path):
        try:
            current_video_id = video_path.split("/")[-1].split(".")[0]
            os.makedirs("data/labelled", exist_ok=True)
            file_path = os.path.join("data", "labelled", f"{current_video_id}.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
            else:
                existing_data = {"video_id": current_video_id, "total_frames": self.total_frames, "events": []}
            
            self.events = existing_data["events"]
            return gr.update(value=json.dumps(existing_data, indent=2), language="json")
        
        except Exception as e:
            gr.Warning(f"Error loading event list: {e}")
            return gr.update(value=None)
    
    def get_court_position(self, x: int, y: int) -> str:
        if y < self.net[1]:
            return 'Far deuce' if x < self.net[0] else 'Far ad'
        else:
            return 'Near ad' if x < self.net[0] else 'Near deuce'
        
    def handle_image_click(self, evt: gr.SelectData):
        try:
            if evt is None or evt.index is None:
                gr.Warning("Please click on the video frame.")
                return None, None
            x, y = evt.index
            court_pos = self.get_court_position(x, y)
            return gr.update(value=court_pos), gr.update(value=[x, y])
        
        except Exception as e:
            gr.Warning(f"Error occured while processing: {e}")
            return None, None