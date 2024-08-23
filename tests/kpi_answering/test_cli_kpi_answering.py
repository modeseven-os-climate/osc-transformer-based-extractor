from typer.testing import CliRunner
from unittest.mock import patch
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import pytest

from src.osc_transformer_based_extractor.kpi_answering.cli_kpi_answering import (
    kpi_answering_app,
)

runner = CliRunner()


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for the test.
    """
    with TemporaryDirectory() as temp_dir:
        yield temp_dir
        # Clean up the temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


@patch(
    "src.osc_transformer_based_extractor.kpi_answering.train_kpi_answering.train_kpi_answering"
)
@patch(
    "src.osc_transformer_based_extractor.kpi_answering.train_kpi_answering.check_csv_columns_kpi_answering"
)
@patch(
    "src.osc_transformer_based_extractor.kpi_answering.train_kpi_answering.check_output_dir"
)
def test_fine_tune_kpi_answering(
    mock_check_output_dir,
    mock_check_csv_columns_kpi_answering,
    mock_train_kpi_answering,
    temp_dir,
):
    """
    Test the fine-tune command.
    """
    data_path = Path(temp_dir) / "train_data.csv"
    model_name = "distilbert-base-uncased"
    max_length = 128
    epochs = 3
    batch_size = 16
    output_dir = Path(temp_dir) / "output_model"
    save_steps = 500

    result = runner.invoke(
        kpi_answering_app,
        [
            "fine-tune",
            str(data_path),
            model_name,
            str(max_length),
            str(epochs),
            str(batch_size),
            str(output_dir),
            str(save_steps),
        ],
    )

    assert result.exit_code == 0
    mock_check_csv_columns_kpi_answering.assert_called_once_with(data_path)
    mock_check_output_dir.assert_called_once_with(output_dir)
    mock_train_kpi_answering.assert_called_once_with(
        data_path=str(data_path),
        model_name=model_name,
        max_length=max_length,
        epochs=epochs,
        batch_size=batch_size,
        output_dir=str(output_dir),
        save_steps=save_steps,
    )
    assert (
        f"Model '{model_name}' trained and saved successfully at {output_dir}"
        in result.output
    )


@patch(
    "src.osc_transformer_based_extractor.kpi_answering.inference_kpi_answering.run_full_inference_kpi_answering"
)
@patch(
    "src.osc_transformer_based_extractor.kpi_answering.inference_kpi_answering.validate_path_exists"
)
def test_inference_kpi_answering(
    mock_validate_path_exists, mock_run_full_inference_kpi_answering, temp_dir
):
    """
    Test the inference command.
    """
    data_file_path = Path(temp_dir) / "test_data.csv"
    output_path = Path(temp_dir) / "output"
    model_path = "distilbert-base-uncased-distilled-squad"

    result = runner.invoke(
        kpi_answering_app,
        ["inference", str(data_file_path), str(output_path), model_path],
    )

    assert result.exit_code == 0
    assert "Inference completed successfully!" in result.output
    mock_validate_path_exists.assert_any_call(data_file_path, "data_file_path")
    mock_validate_path_exists.assert_any_call(output_path, "output_path")
    mock_validate_path_exists.assert_any_call(model_path, "model_path")
    mock_run_full_inference_kpi_answering.assert_called_once_with(
        data_file_path=str(data_file_path),
        output_path=str(output_path),
        model_path=model_path,
    )
