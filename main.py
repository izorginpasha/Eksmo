from core.scene_optimizer import compress_sfx_by_scene


def main():
    compress_sfx_by_scene(
        input_path="output/events.json",
        output_path="output/compressed_sfx.json",
        model_name="mistral:latest"
    )

if __name__=="__main__":
    main()