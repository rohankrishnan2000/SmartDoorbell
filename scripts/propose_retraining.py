from edge.training.self_correction_loop import SelfCorrectionLoop


def main() -> None:
    proposal = SelfCorrectionLoop().propose("package_theft_risk", 0.78, human_label="visitor_detected")
    print(proposal)


if __name__ == "__main__":
    main()

